# Generated by Django 4.0.1 on 2022-02-24 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotels', '0005_hotel_available_rooms_hotel_total_rooms'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imagemodel',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='hotel'),
        ),
    ]
