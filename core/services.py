from django.db.models import Q
from .models import Reservation, RoomBlock, HousekeepingTask, ReviewRequest


def overlap_q(date_in, date_out):
    return Q(date_in__lt=date_out, date_out__gt=date_in)


def has_reservation_conflict(hotel, room, date_in, date_out, exclude_id=None):
    qs = Reservation.objects.filter(hotel=hotel, room=room).exclude(status=Reservation.STATUS_CANCELLED).filter(overlap_q(date_in, date_out))
    if exclude_id:
        qs = qs.exclude(id=exclude_id)
    return qs.exists()


def has_block_conflict(hotel, room, date_in, date_out, exclude_id=None):
    qs = RoomBlock.objects.filter(hotel=hotel, room=room).filter(overlap_q(date_in, date_out))
    if exclude_id:
        qs = qs.exclude(id=exclude_id)
    return qs.exists()


def ensure_checkout_side_effects(reservation):
    HousekeepingTask.objects.update_or_create(
        hotel=reservation.hotel,
        room=reservation.room,
        for_date=reservation.date_out,
        defaults={'status': HousekeepingTask.STATUS_PENDING},
    )
    ReviewRequest.objects.get_or_create(
        hotel=reservation.hotel,
        reservation=reservation,
        defaults={'token': ReviewRequest.generate_token(), 'status': ReviewRequest.STATUS_PENDING},
    )
