# PMS + Reseñas (Django + HTMX)

## Requisitos
- Python 3.12+
- PostgreSQL (objetivo principal) o sqlite solo para desarrollo rápido

## Puesta en marcha (manual)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo
python manage.py runserver
```

## Crear usuario de hotel
```bash
python manage.py create_hotel_user --email admin@hotel.com --password secret123 --hotel "Hotel Demo"
```

## Navegación
- Calendario
- Reservas
- Hoy
- Limpieza
- Reseñas
- Ajustes
