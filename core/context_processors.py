def navigation(request):
    return {
        'main_nav': [
            ('calendar', 'Calendario'),
            ('reservations', 'Reservas'),
            ('today', 'Hoy'),
            ('housekeeping', 'Limpieza'),
            ('reviews', 'Reseñas'),
            ('settings_page', 'Ajustes'),
        ]
    }
