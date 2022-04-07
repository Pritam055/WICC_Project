from email.policy import default
from django.db import models
from django.contrib.auth.models import AbstractUser 
from django.conf import settings

# Create your models here.

USER_TYPE = (
    ('customer', 'Customer/Guest'),
    ('hotel_owner', 'Hotel Owner')
)

class CustomUser(AbstractUser):

    email = models.EmailField(unique=True)
    address = models.CharField(max_length=100, blank=False, null=False)
    phone = models.CharField(max_length=10, blank=False, null=False)
    user_type = models.CharField(max_length=15, blank=False, null=False, choices=USER_TYPE, default='customer')
    verified = models.BooleanField(default=False)
    forget_password_token = models.CharField(max_length=254, null=True, blank=True)

    class Meta:
        verbose_name = "Custom User"
        verbose_name_plural = "Custom Users"

    def get_user_type(self):
        return self.user_type
        # return USER_TYPE[int(self.user_type)][1]
    
    @property
    def is_hotelOwner(self): 
        return self.groups.filter(name='hotelOwner-gang').exists() 

class Certificate(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='certificate', null=False, blank=False) 

    