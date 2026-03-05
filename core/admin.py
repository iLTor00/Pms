from django.contrib import admin
from .models import Hotel, Room, Reservation, RoomBlock, HousekeepingTask, ReviewRequest, ReviewResponse, Profile

admin.site.register([Hotel, Room, Reservation, RoomBlock, HousekeepingTask, ReviewRequest, ReviewResponse, Profile])
