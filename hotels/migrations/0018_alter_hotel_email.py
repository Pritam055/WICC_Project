# Generated by Django 4.0.1 on 2022-03-15 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotels', '0017_alter_comment_hotel_alter_reservation_payment_method'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hotel',
            name='email',
            field=models.CharField(max_length=200, null=True, unique=True),
        ),
    ]
