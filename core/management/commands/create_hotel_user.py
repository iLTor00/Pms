from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from core.models import Hotel, Profile


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--email', required=True)
        parser.add_argument('--password', required=True)
        parser.add_argument('--hotel', required=True)

    def handle(self, *args, **options):
        User = get_user_model()
        hotel, _ = Hotel.objects.get_or_create(name=options['hotel'])
        if User.objects.filter(username=options['email']).exists():
            raise CommandError('El usuario ya existe')
        user = User.objects.create_user(username=options['email'], email=options['email'], password=options['password'])
        Profile.objects.create(user=user, hotel=hotel)
        self.stdout.write(self.style.SUCCESS(f'Usuario creado para {hotel.name}'))
