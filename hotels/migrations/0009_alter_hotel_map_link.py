# Generated by Django 4.0.1 on 2022-02-25 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotels', '0008_rename_check_in_reservation_checkin_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hotel',
            name='map_link',
            field=models.TextField(blank=True, null=True),
        ),
    ]