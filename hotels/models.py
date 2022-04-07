 
from django.db import models
from django.conf import settings
from django.urls import reverse 

# from accounts.models import CustomUser

# Create your models here.

class Hotel(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)
    address = models.CharField(max_length=100)
    phone = models.CharField(max_length=10, null=True)
    email = models.CharField(max_length=200, null=True, unique=True)
    total_rooms = models.PositiveIntegerField(default=0)
    available_rooms = models.PositiveIntegerField(default=0)
    room_price = models.PositiveIntegerField(default=0)
    rate = models.PositiveIntegerField(default = 0)
    established = models.DateField()
    description = models.TextField(null=True, blank=True)
    # map_link = models.URLField(max_length=200, null=True, blank=True)
    map_link = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.name}"

    def get_absolute_url(self):  
        return reverse('hotels:hotel_detail', kwargs={'pk': self.pk})


class ImageModel(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='hotel_images')
    image = models.ImageField(upload_to='hotel', null=True, blank=True)

PAYMENT_METHOD = (
    ('online_pay', 'Online Pay'),
    ('offline_pay', 'Offline Pay')
)

"""RESERVATION_STATUS = (
    ('pending', 'pending'),
    ('completed', 'completed')
)"""

RESERVATION_STATUS = (
    ('reserved', 'reserved'),
    ('checked_in', 'checked_in'),
    ('checked_out', 'checked_out')
)

class Reservation(models.Model):
    no_of_rooms = models.PositiveIntegerField(default=0)
    reserved_date = models.DateTimeField(auto_now_add = True)
    checkin_date = models.DateTimeField(blank=True, null=True)
    checkout_date = models.DateTimeField(blank=True, null=True)
    amount = models.PositiveIntegerField(default=0)
    paid = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=15, choices=PAYMENT_METHOD, default='offline_pay')
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='customer_reservations')
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='hotel_reservations')
    phone = models.CharField(max_length=10)   
    checkin_status =  models.CharField(max_length=15, choices=RESERVATION_STATUS, default="reserved")

    @property
    def get_CustomerName(self):
        return self.customer.username 

    @property
    def get_HotelName(self):
        return self.hotel.name

class Comment(models.Model):
    content = models.CharField(max_length=250, blank=False, null=False)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='hotel_comments')
    date_time = models.DateTimeField(auto_now_add=True)
