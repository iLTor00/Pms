import csv
from datetime import timedelta
from urllib.parse import quote
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db.models import Q, Avg
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_POST
from .forms import ReservationForm, RoomBlockForm, HotelForm, RoomForm
from .models import Profile, Room, Reservation, RoomBlock, HousekeepingTask, ReviewRequest, ReviewResponse
from .services import ensure_checkout_side_effects, overlap_q


class LoginPageView(LoginView):
    template_name = 'auth/login.html'


def logout_view(request):
    logout(request)
    return redirect('login')


def user_hotel(user):
    return user.profile.hotel


def get_days(request):
    try:
        days = int(request.GET.get('days', 7))
    except ValueError:
        days = 7
    return days if days in [7, 14, 30] else 7


@login_required
def calendar_view(request):
    hotel = user_hotel(request.user)
    start = parse_date(request.GET.get('start', '')) or timezone.localdate()
    days = get_days(request)
    end = start + timedelta(days=days)
    rooms = Room.objects.filter(hotel=hotel, is_active=True).order_by('code')
    reservations = Reservation.objects.filter(hotel=hotel, status__in=['reserved', 'checked_in'], date_in__lt=end, date_out__gt=start).select_related('room')
    blocks = RoomBlock.objects.filter(hotel=hotel, date_in__lt=end, date_out__gt=start).select_related('room')
    q = request.GET.get('q', '').strip()
    search = Reservation.objects.none()
    if q:
        search = Reservation.objects.filter(hotel=hotel).filter(Q(guest_name__icontains=q) | Q(guest_phone__icontains=q)).select_related('room')[:10]
    dates = [start + timedelta(days=i) for i in range(days)]
    return render(request, 'core/calendar.html', locals())


@login_required
def reservation_create_modal(request):
    hotel = user_hotel(request.user)
    initial = {'room': request.GET.get('room'), 'date_in': request.GET.get('date_in')}
    form = ReservationForm(request.POST or None, hotel=hotel, initial=initial)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.hotel = hotel
        obj.save()
        return HttpResponse('<script>window.location.reload()</script>')
    return render(request, 'partials/reservation_form_modal.html', {'form': form, 'title': 'Nueva reserva'})


@login_required
def reservation_detail_modal(request, reservation_id):
    hotel = user_hotel(request.user)
    reservation = get_object_or_404(Reservation.objects.select_related('room'), id=reservation_id, hotel=hotel)
    return render(request, 'partials/reservation_detail_modal.html', {'reservation': reservation})


@login_required
def reservation_edit_modal(request, reservation_id):
    hotel = user_hotel(request.user)
    reservation = get_object_or_404(Reservation, id=reservation_id, hotel=hotel)
    form = ReservationForm(request.POST or None, instance=reservation, hotel=hotel)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return HttpResponse('<script>window.location.reload()</script>')
    return render(request, 'partials/reservation_form_modal.html', {'form': form, 'title': 'Editar reserva'})


@login_required
@require_POST
def reservation_checkin(request, reservation_id):
    hotel = user_hotel(request.user)
    r = get_object_or_404(Reservation, id=reservation_id, hotel=hotel)
    if r.status == 'reserved':
        r.status = 'checked_in'
        r.save(update_fields=['status', 'updated_at'])
    return redirect(request.META.get('HTTP_REFERER', 'reservations'))


@login_required
@require_POST
def reservation_checkout(request, reservation_id):
    hotel = user_hotel(request.user)
    r = get_object_or_404(Reservation, id=reservation_id, hotel=hotel)
    if r.status == 'checked_in':
        r.status = 'checked_out'
        r.save(update_fields=['status', 'updated_at'])
        ensure_checkout_side_effects(r)
    return redirect(request.META.get('HTTP_REFERER', 'reservations'))


@login_required
@require_POST
def reservation_cancel(request, reservation_id):
    hotel = user_hotel(request.user)
    r = get_object_or_404(Reservation, id=reservation_id, hotel=hotel)
    r.status = 'cancelled'
    r.save(update_fields=['status', 'updated_at'])
    return redirect(request.META.get('HTTP_REFERER', 'reservations'))


@login_required
def block_create_modal(request):
    hotel = user_hotel(request.user)
    form = RoomBlockForm(request.POST or None, hotel=hotel, initial={'room': request.GET.get('room'), 'date_in': request.GET.get('date_in')})
    if request.method == 'POST' and form.is_valid():
        b = form.save(commit=False)
        b.hotel = hotel
        b.save()
        return HttpResponse('<script>window.location.reload()</script>')
    return render(request, 'partials/block_form_modal.html', {'form': form, 'title': 'Nuevo bloqueo'})


@login_required
def block_detail_modal(request, block_id):
    hotel = user_hotel(request.user)
    block = get_object_or_404(RoomBlock.objects.select_related('room'), id=block_id, hotel=hotel)
    return render(request, 'partials/block_detail_modal.html', {'block': block})


@login_required
def block_edit_modal(request, block_id):
    hotel = user_hotel(request.user)
    block = get_object_or_404(RoomBlock, id=block_id, hotel=hotel)
    form = RoomBlockForm(request.POST or None, instance=block, hotel=hotel)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return HttpResponse('<script>window.location.reload()</script>')
    return render(request, 'partials/block_form_modal.html', {'form': form, 'title': 'Editar bloqueo'})


@login_required
def reservations_view(request):
    hotel = user_hotel(request.user)
    tab = request.GET.get('tab', 'proximas')
    q = request.GET.get('q', '').strip()
    today = timezone.localdate()
    qs = Reservation.objects.filter(hotel=hotel).select_related('room').order_by('date_in')
    if q:
        qs = qs.filter(Q(guest_name__icontains=q) | Q(guest_phone__icontains=q))
    if tab == 'en_curso':
        qs = qs.filter(status='checked_in')
    elif tab == 'finalizadas':
        qs = qs.filter(status='checked_out')
    elif tab == 'canceladas':
        qs = qs.filter(status='cancelled')
    else:
        qs = qs.filter(status='reserved', date_out__gte=today)
    return render(request, 'core/reservations.html', {'reservations': qs, 'tab': tab, 'q': q})

@login_required
def today_view(request):
    hotel = user_hotel(request.user)
    today = timezone.localdate()
    checkins = Reservation.objects.filter(hotel=hotel, date_in=today, status='reserved').select_related('room')
    checkouts = Reservation.objects.filter(hotel=hotel, date_out=today, status='checked_in').select_related('room')
    cleaning = HousekeepingTask.objects.filter(hotel=hotel, for_date=today, status__in=['pending', 'cleaning']).select_related('room')
    return render(request, 'core/today.html', {'checkins': checkins, 'checkouts': checkouts, 'cleaning': cleaning})

@login_required
def housekeeping_view(request):
    hotel = user_hotel(request.user)
    today = timezone.localdate()
    pending = HousekeepingTask.objects.filter(hotel=hotel, for_date=today, status='pending').select_related('room')
    cleaning = HousekeepingTask.objects.filter(hotel=hotel, for_date=today, status='cleaning').select_related('room')
    ready = HousekeepingTask.objects.filter(hotel=hotel, for_date=today, status='ready').select_related('room')
    return render(request, 'core/housekeeping.html', {'pending': pending, 'cleaning': cleaning, 'ready': ready})

@login_required
def reviews_view(request):
    hotel = user_hotel(request.user)
    tab = request.GET.get('tab', 'pending')
    today = timezone.localdate()
    since_30 = today - timedelta(days=30)
    kpi_solicitudes = ReviewRequest.objects.filter(hotel=hotel, created_at__date=today).count()
    kpi_respondidas = ReviewResponse.objects.filter(hotel=hotel, created_at__date=today).count()
    kpi_promedio = ReviewResponse.objects.filter(hotel=hotel, created_at__date__gte=since_30).aggregate(v=Avg('score'))['v'] or 0
    kpi_privado = ReviewResponse.objects.filter(hotel=hotel, created_at__date__gte=since_30, routed_public=False).count()
    base = ReviewRequest.objects.filter(hotel=hotel).select_related('reservation__room').order_by('-created_at')
    if tab == 'sent':
        requests = base.filter(status='sent')
    elif tab == 'responded':
        requests = base.filter(status='responded')
    elif tab == 'private':
        requests = base.filter(status='responded', reservation__reviewresponse__score__lte=3).distinct()
    else:
        requests = base.filter(status='pending')
    review_rows = []
    for rr in requests:
        landing = request.build_absolute_uri(f"/r/{rr.token}/")
        phone = (rr.reservation.guest_phone or '').replace('+', '').replace(' ', '')
        message = quote(f"Hola, ¿nos compartís tu experiencia? {landing}")
        wa_url = f"https://wa.me/{phone}?text={message}" if phone else ''
        review_rows.append({'obj': rr, 'wa_url': wa_url, 'response': ReviewResponse.objects.filter(token=rr.token).first()})
    return render(request, 'core/reviews.html', locals())

@login_required
def settings_page(request):
    hotel = user_hotel(request.user)
    hotel_form = HotelForm(request.POST or None, instance=hotel, prefix='hotel')
    room_form = RoomForm(request.POST or None, prefix='room')
    if request.method == 'POST' and 'save_hotel' in request.POST and hotel_form.is_valid():
        hotel_form.save()
        return redirect('settings_page')
    rooms = Room.objects.filter(hotel=hotel).order_by('code')
    return render(request, 'core/settings.html', {'hotel_form': hotel_form, 'room_form': room_form, 'rooms': rooms})

def review_landing(request, token):
    rr = get_object_or_404(ReviewRequest.objects.select_related('hotel', 'reservation'), token=token)
    already = ReviewResponse.objects.filter(token=token).first()
    if already:
        return render(request, 'core/review_done.html', {'response': already, 'hotel': rr.hotel})
    if request.method == 'POST':
        score = int(request.POST.get('score'))
        feedback = request.POST.get('feedback', '').strip()
        routed_public = score >= 4
        ReviewResponse.objects.create(hotel=rr.hotel, reservation=rr.reservation, token=token, score=score, feedback=feedback if not routed_public else '', routed_public=routed_public)
        rr.status = 'responded'
        rr.save(update_fields=['status'])
        if routed_public:
            return render(request, 'core/review_public.html', {'hotel': rr.hotel})
        return render(request, 'core/review_private.html', {'hotel': rr.hotel})
    return render(request, 'core/review_landing.html', {'token': token, 'hotel': rr.hotel})

@login_required
def availability_check(request):
    hotel = user_hotel(request.user)
    date_in = parse_date(request.GET.get('date_in', ''))
    date_out = parse_date(request.GET.get('date_out', ''))
    if not date_in or not date_out or date_out <= date_in:
        return HttpResponse('La salida debe ser después de la entrada.')
    free = []
    for room in Room.objects.filter(hotel=hotel, is_active=True):
        occ = Reservation.objects.filter(hotel=hotel, room=room).exclude(status='cancelled').filter(overlap_q(date_in, date_out)).exists()
        blk = RoomBlock.objects.filter(hotel=hotel, room=room).filter(overlap_q(date_in, date_out)).exists()
        if not occ and not blk:
            free.append(room.code)
    if free:
        return HttpResponse('Sí, libres: ' + ', '.join(free))
    return HttpResponse('No hay habitaciones disponibles.')

@login_required
@require_POST
def housekeeping_start(request, task_id):
    hotel = user_hotel(request.user)
    task = get_object_or_404(HousekeepingTask, id=task_id, hotel=hotel)
    task.status = 'cleaning'
    task.save(update_fields=['status', 'updated_at'])
    if request.headers.get('HX-Request'):
        return housekeeping_view(request)
    return redirect('housekeeping')

@login_required
@require_POST
def housekeeping_ready(request, task_id):
    hotel = user_hotel(request.user)
    task = get_object_or_404(HousekeepingTask, id=task_id, hotel=hotel)
    task.status = 'ready'
    task.save(update_fields=['status', 'updated_at'])
    if request.headers.get('HX-Request'):
        return housekeeping_view(request)
    return redirect('housekeeping')

@login_required
@require_POST
def mark_review_sent(request, req_id):
    hotel = user_hotel(request.user)
    rr = get_object_or_404(ReviewRequest, id=req_id, hotel=hotel)
    rr.status = 'sent'
    rr.sent_at = timezone.now()
    rr.save(update_fields=['status', 'sent_at'])
    return redirect('reviews')

@login_required
def room_create(request):
    hotel = user_hotel(request.user)
    form = RoomForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        room = form.save(commit=False)
        room.hotel = hotel
        room.save()
    return redirect('settings_page')

@login_required
def room_edit(request, room_id):
    hotel = user_hotel(request.user)
    room = get_object_or_404(Room, id=room_id, hotel=hotel)
    form = RoomForm(request.POST or None, instance=room)
    if request.method == 'POST' and form.is_valid():
        form.save()
    return redirect('settings_page')

@login_required
@require_POST
def room_toggle(request, room_id):
    hotel = user_hotel(request.user)
    room = get_object_or_404(Room, id=room_id, hotel=hotel)
    room.is_active = not room.is_active
    room.save(update_fields=['is_active', 'updated_at'])
    return redirect('settings_page')

@login_required
def export_reservations_csv(request):
    hotel = user_hotel(request.user)
    res = Reservation.objects.filter(hotel=hotel).select_related('room').order_by('date_in')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=reservas.csv'
    w = csv.writer(response)
    w.writerow(['huesped', 'habitacion', 'entrada', 'salida', 'estado', 'telefono', 'email', 'fuente'])
    for r in res:
        w.writerow([r.guest_name, r.room.code, r.date_in, r.date_out, r.status, r.guest_phone, r.guest_email, r.source])
    return response
