from django.urls import path
from core import views

urlpatterns = [
    path('', views.calendar_view, name='calendar'),
    path('reservas/', views.reservations_view, name='reservations'),
    path('reservas/modal/nueva/', views.reservation_create_modal, name='reservation_create_modal'),
    path('reservas/modal/<uuid:reservation_id>/', views.reservation_detail_modal, name='reservation_detail_modal'),
    path('reservas/modal/<uuid:reservation_id>/editar/', views.reservation_edit_modal, name='reservation_edit_modal'),
    path('reservas/<uuid:reservation_id>/checkin/', views.reservation_checkin, name='reservation_checkin'),
    path('reservas/<uuid:reservation_id>/checkout/', views.reservation_checkout, name='reservation_checkout'),
    path('reservas/<uuid:reservation_id>/anular/', views.reservation_cancel, name='reservation_cancel'),
    path('bloqueos/modal/nuevo/', views.block_create_modal, name='block_create_modal'),
    path('bloqueos/modal/<uuid:block_id>/', views.block_detail_modal, name='block_detail_modal'),
    path('bloqueos/modal/<uuid:block_id>/editar/', views.block_edit_modal, name='block_edit_modal'),
    path('hoy/', views.today_view, name='today'),
    path('hoy/hay-lugar/', views.availability_check, name='availability_check'),
    path('limpieza/', views.housekeeping_view, name='housekeeping'),
    path('limpieza/<uuid:task_id>/empezar/', views.housekeeping_start, name='housekeeping_start'),
    path('limpieza/<uuid:task_id>/lista/', views.housekeeping_ready, name='housekeeping_ready'),
    path('resenas/', views.reviews_view, name='reviews'),
    path('resenas/<uuid:req_id>/enviado/', views.mark_review_sent, name='mark_review_sent'),
    path('ajustes/', views.settings_page, name='settings_page'),
    path('ajustes/habitacion/nueva/', views.room_create, name='room_create'),
    path('ajustes/habitacion/<uuid:room_id>/editar/', views.room_edit, name='room_edit'),
    path('ajustes/habitacion/<uuid:room_id>/toggle/', views.room_toggle, name='room_toggle'),
    path('ajustes/exportar-reservas.csv', views.export_reservations_csv, name='export_reservations_csv'),
]
