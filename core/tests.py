from datetime import date
from django.contrib.auth import get_user_model
from django.test import TestCase
from .models import Hotel, Room, Reservation, RoomBlock, HousekeepingTask, ReviewRequest, ReviewResponse, Profile
from .services import has_reservation_conflict, has_block_conflict, ensure_checkout_side_effects


class CoreLogicTests(TestCase):
    def setUp(self):
        self.hotel = Hotel.objects.create(name='H1')
        self.room = Room.objects.create(hotel=self.hotel, code='101')
        self.r = Reservation.objects.create(hotel=self.hotel, room=self.room, guest_name='A', date_in=date(2026,1,1), date_out=date(2026,1,4), status='reserved')

    def test_overlap_conflicts(self):
        self.assertTrue(has_reservation_conflict(self.hotel, self.room, date(2026,1,3), date(2026,1,5)))
        self.assertFalse(has_reservation_conflict(self.hotel, self.room, date(2026,1,4), date(2026,1,5)))
        RoomBlock.objects.create(hotel=self.hotel, room=self.room, date_in=date(2026,1,5), date_out=date(2026,1,7))
        self.assertTrue(has_block_conflict(self.hotel, self.room, date(2026,1,6), date(2026,1,8)))

    def test_transitions(self):
        self.client.force_login(self._user())
        self.client.post(f'/reservas/{self.r.id}/checkin/')
        self.r.refresh_from_db()
        self.assertEqual(self.r.status, 'checked_in')
        self.client.post(f'/reservas/{self.r.id}/checkout/')
        self.r.refresh_from_db()
        self.assertEqual(self.r.status, 'checked_out')

    def test_checkout_side_effects_idempotent(self):
        self.r.status = 'checked_in'
        self.r.save()
        ensure_checkout_side_effects(self.r)
        ensure_checkout_side_effects(self.r)
        self.assertEqual(HousekeepingTask.objects.filter(hotel=self.hotel, room=self.room, for_date=self.r.date_out).count(), 1)
        self.assertEqual(ReviewRequest.objects.filter(reservation=self.r).count(), 1)

    def test_guest_landing_routing_and_token_reuse(self):
        req = ReviewRequest.objects.create(hotel=self.hotel, reservation=self.r, token='t1')
        resp = self.client.get('/r/t1/')
        self.assertEqual(resp.status_code, 200)
        self.client.post('/r/t1/', {'score': '5'})
        self.assertEqual(ReviewResponse.objects.filter(token='t1').count(), 1)
        self.client.post('/r/t1/', {'score': '3', 'feedback': 'mal'})
        self.assertEqual(ReviewResponse.objects.filter(token='t1').count(), 1)

    def _user(self):
        u = get_user_model().objects.create_user(username='u', password='p')
        Profile.objects.create(user=u, hotel=self.hotel)
        return u
