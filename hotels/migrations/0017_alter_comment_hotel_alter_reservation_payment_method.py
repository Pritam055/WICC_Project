# Generated by Django 4.0.1 on 2022-03-12 16:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hotels', '0016_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='hotel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hotel_comments', to='hotels.hotel'),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='payment_method',
            field=models.CharField(choices=[('online_pay', 'Online Pay'), ('offline_pay', 'Offline Pay')], default='offline_pay', max_length=15),
        ),
    ]
