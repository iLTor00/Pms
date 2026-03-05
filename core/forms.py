from django import forms
from django.core.exceptions import ValidationError
from .models import Reservation, RoomBlock, Hotel, Room
from .services import has_reservation_conflict, has_block_conflict

CONFLICT_MSG = 'Esa habitación ya está ocupada en esas fechas.'
INVALID_DATES_MSG = 'La salida debe ser después de la entrada.'


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['room', 'guest_name', 'guest_phone', 'guest_email', 'date_in', 'date_out', 'source', 'notes']

    def __init__(self, *args, **kwargs):
        self.hotel = kwargs.pop('hotel')
        super().__init__(*args, **kwargs)
        self.fields['room'].queryset = Room.objects.filter(hotel=self.hotel, is_active=True)

    def clean(self):
        data = super().clean()
        if data.get('date_in') and data.get('date_out') and data['date_out'] <= data['date_in']:
            raise ValidationError(INVALID_DATES_MSG)
        room = data.get('room')
        if room and data.get('date_in') and data.get('date_out'):
            if has_reservation_conflict(self.hotel, room, data['date_in'], data['date_out'], getattr(self.instance, 'id', None)):
                raise ValidationError(CONFLICT_MSG)
            if has_block_conflict(self.hotel, room, data['date_in'], data['date_out']):
                raise ValidationError(CONFLICT_MSG)
        return data


class RoomBlockForm(forms.ModelForm):
    class Meta:
        model = RoomBlock
        fields = ['room', 'date_in', 'date_out', 'reason']

    def __init__(self, *args, **kwargs):
        self.hotel = kwargs.pop('hotel')
        super().__init__(*args, **kwargs)
        self.fields['room'].queryset = Room.objects.filter(hotel=self.hotel, is_active=True)

    def clean(self):
        data = super().clean()
        if data.get('date_in') and data.get('date_out') and data['date_out'] <= data['date_in']:
            raise ValidationError(INVALID_DATES_MSG)
        room = data.get('room')
        if room and data.get('date_in') and data.get('date_out'):
            if has_block_conflict(self.hotel, room, data['date_in'], data['date_out'], getattr(self.instance, 'id', None)):
                raise ValidationError(CONFLICT_MSG)
            if has_reservation_conflict(self.hotel, room, data['date_in'], data['date_out']):
                raise ValidationError(CONFLICT_MSG)
        return data


class HotelForm(forms.ModelForm):
    class Meta:
        model = Hotel
        fields = ['name', 'checkin_time', 'checkout_time', 'google_review_url']


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['code', 'type', 'capacity', 'is_active']
