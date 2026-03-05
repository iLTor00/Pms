from django.conf import settings
from django.db import migrations, models
import django.core.validators
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name='Hotel',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.TextField()),
                ('timezone', models.TextField(default='America/Argentina/Buenos_Aires')),
                ('checkin_time', models.TimeField(default='14:00')),
                ('checkout_time', models.TimeField(default='10:00')),
                ('google_review_url', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('code', models.TextField()),
                ('type', models.TextField(blank=True, null=True)),
                ('capacity', models.IntegerField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('hotel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.hotel')),
            ],
            options={'unique_together': {('hotel', 'code')}},
        ),
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('guest_name', models.TextField()),
                ('guest_phone', models.TextField(blank=True, null=True)),
                ('guest_email', models.TextField(blank=True, null=True)),
                ('date_in', models.DateField()),
                ('date_out', models.DateField()),
                ('status', models.TextField(choices=[('reserved', 'reserved'), ('checked_in', 'checked_in'), ('checked_out', 'checked_out'), ('cancelled', 'cancelled')], default='reserved')),
                ('source', models.TextField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('hotel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.hotel')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.room')),
            ],
        ),
        migrations.CreateModel(
            name='RoomBlock',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('date_in', models.DateField()),
                ('date_out', models.DateField()),
                ('reason', models.TextField(blank=True, null=True)),
                ('hotel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.hotel')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.room')),
            ],
        ),
        migrations.CreateModel(
            name='HousekeepingTask',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('for_date', models.DateField()),
                ('status', models.TextField(choices=[('pending', 'pending'), ('cleaning', 'cleaning'), ('ready', 'ready')], default='pending')),
                ('note', models.TextField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('hotel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.hotel')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.room')),
            ],
            options={'unique_together': {('hotel', 'room', 'for_date')}},
        ),
        migrations.CreateModel(
            name='ReviewRequest',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('channel', models.TextField(choices=[('whatsapp_link', 'whatsapp_link'), ('email', 'email')], default='whatsapp_link')),
                ('sent_at', models.DateTimeField(blank=True, null=True)),
                ('status', models.TextField(choices=[('pending', 'pending'), ('sent', 'sent'), ('responded', 'responded')], default='pending')),
                ('token', models.TextField(unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('hotel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.hotel')),
                ('reservation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.reservation')),
            ],
        ),
        migrations.CreateModel(
            name='ReviewResponse',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('token', models.TextField()),
                ('score', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('feedback', models.TextField(blank=True, null=True)),
                ('routed_public', models.BooleanField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('hotel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.hotel')),
                ('reservation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.reservation')),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('hotel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.hotel')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddIndex(model_name='reservation', index=models.Index(fields=['hotel', 'room', 'date_in'], name='core_reserv_hotel_i_71f2f8_idx')),
        migrations.AddIndex(model_name='reservation', index=models.Index(fields=['hotel', 'room', 'date_out'], name='core_reserv_hotel_i_1bdb0f_idx')),
        migrations.AddIndex(model_name='reservation', index=models.Index(fields=['hotel', 'status'], name='core_reserv_hotel_i_fffd0f_idx')),
        migrations.AddIndex(model_name='roomblock', index=models.Index(fields=['hotel', 'room', 'date_in'], name='core_roombl_hotel_i_9f7a5a_idx')),
        migrations.AddIndex(model_name='roomblock', index=models.Index(fields=['hotel', 'room', 'date_out'], name='core_roombl_hotel_i_24947b_idx')),
        migrations.AddIndex(model_name='housekeepingtask', index=models.Index(fields=['hotel', 'for_date', 'status'], name='core_housek_hotel_i_4c9705_idx')),
        migrations.AddIndex(model_name='reviewrequest', index=models.Index(fields=['hotel', 'status', 'created_at'], name='core_review_hotel_i_13dd68_idx')),
        migrations.AddIndex(model_name='reviewresponse', index=models.Index(fields=['hotel', 'created_at'], name='core_review_hotel_i_41415c_idx')),
    ]
