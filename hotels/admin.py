from django.contrib import admin

from .models import Reservation, Hotel, ImageModel, Comment
# Register your models here.

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('name','owner', 'address', 'owner')

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('hotel','id','customer', 'no_of_rooms','checkin_status')

admin.site.register(ImageModel)
admin.site.register(Comment)