import secrets
import uuid
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Hotel(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField()
    timezone = models.TextField(default='America/Argentina/Buenos_Aires')
    checkin_time = models.TimeField(default='14:00')
    checkout_time = models.TimeField(default='10:00')
    google_review_url = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Room(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    code = models.TextField()
    type = models.TextField(null=True, blank=True)
    capacity = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('hotel', 'code')

    def __str__(self):
        return self.code


class Reservation(TimeStampedModel):
    STATUS_RESERVED = 'reserved'
    STATUS_CHECKED_IN = 'checked_in'
    STATUS_CHECKED_OUT = 'checked_out'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_RESERVED, 'reserved'),
        (STATUS_CHECKED_IN, 'checked_in'),
        (STATUS_CHECKED_OUT, 'checked_out'),
        (STATUS_CANCELLED, 'cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    guest_name = models.TextField()
    guest_phone = models.TextField(null=True, blank=True)
    guest_email = models.TextField(null=True, blank=True)
    date_in = models.DateField()
    date_out = models.DateField()
    status = models.TextField(choices=STATUS_CHOICES, default=STATUS_RESERVED)
    source = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['hotel', 'room', 'date_in']),
            models.Index(fields=['hotel', 'room', 'date_out']),
            models.Index(fields=['hotel', 'status']),
        ]


class RoomBlock(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    date_in = models.DateField()
    date_out = models.DateField()
    reason = models.TextField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['hotel', 'room', 'date_in']),
            models.Index(fields=['hotel', 'room', 'date_out']),
        ]


class HousekeepingTask(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_CLEANING = 'cleaning'
    STATUS_READY = 'ready'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'pending'),
        (STATUS_CLEANING, 'cleaning'),
        (STATUS_READY, 'ready'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    for_date = models.DateField()
    status = models.TextField(choices=STATUS_CHOICES, default=STATUS_PENDING)
    note = models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('hotel', 'room', 'for_date')
        indexes = [models.Index(fields=['hotel', 'for_date', 'status'])]


class ReviewRequest(models.Model):
    CHANNEL_WHATSAPP = 'whatsapp_link'
    CHANNEL_EMAIL = 'email'
    CHANNEL_CHOICES = [(CHANNEL_WHATSAPP, 'whatsapp_link'), (CHANNEL_EMAIL, 'email')]
    STATUS_PENDING = 'pending'
    STATUS_SENT = 'sent'
    STATUS_RESPONDED = 'responded'
    STATUS_CHOICES = [(STATUS_PENDING, 'pending'), (STATUS_SENT, 'sent'), (STATUS_RESPONDED, 'responded')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    channel = models.TextField(choices=CHANNEL_CHOICES, default=CHANNEL_WHATSAPP)
    sent_at = models.DateTimeField(null=True, blank=True)
    status = models.TextField(choices=STATUS_CHOICES, default=STATUS_PENDING)
    token = models.TextField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['hotel', 'status', 'created_at'])]

    @staticmethod
    def generate_token():
        return secrets.token_urlsafe(24)


class ReviewResponse(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    token = models.TextField()
    score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    feedback = models.TextField(null=True, blank=True)
    routed_public = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['hotel', 'created_at'])]


class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username
