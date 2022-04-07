# Generated by Django 4.0.1 on 2022-02-25 10:24

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('hotels', '0007_hotel_email_hotel_phone'),
    ]

    operations = [
        migrations.RenameField(
            model_name='reservation',
            old_name='check_in',
            new_name='checkin_date',
        ),
        migrations.RenameField(
            model_name='reservation',
            old_name='check_out',
            new_name='checkout_date',
        ),
        migrations.AddField(
            model_name='hotel',
            name='map_link',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='reservation',
            name='reserved_data',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
