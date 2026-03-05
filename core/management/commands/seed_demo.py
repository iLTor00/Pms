from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Hotel, Room, Reservation, HousekeepingTask, ReviewRequest, Profile


class Command(BaseCommand):
    def handle(self, *args, **options):
        hotel, _ = Hotel.objects.get_or_create(name='Hotel Demo', defaults={'google_review_url': 'https://g.page/r/demo/review'})
        room_codes = ['101', '102', '103', '104', '201', '202', 'Cabaña 1', 'Cabaña 2']
        rooms = [Room.objects.get_or_create(hotel=hotel, code=code)[0] for code in room_codes]
        today = timezone.localdate()
        for i, room in enumerate(rooms[:5]):
            res, _ = Reservation.objects.get_or_create(
                hotel=hotel,
                room=room,
                guest_name=f'Huésped {i+1}',
                date_in=today + timedelta(days=i-1),
                date_out=today + timedelta(days=i+1),
                defaults={'guest_phone': f'54911111111{i}', 'source': 'directo'},
            )
            HousekeepingTask.objects.get_or_create(hotel=hotel, room=room, for_date=today, defaults={'status': 'pending'})
            ReviewRequest.objects.get_or_create(
                hotel=hotel,
                reservation=res,
                defaults={'token': ReviewRequest.generate_token(), 'status': 'pending'},
            )
        User = get_user_model()
        if not User.objects.filter(username='demo@hotel.com').exists():
            user = User.objects.create_user(username='demo@hotel.com', email='demo@hotel.com', password='demo12345')
            Profile.objects.get_or_create(user=user, hotel=hotel)
        self.stdout.write(self.style.SUCCESS('Demo listo'))
