from django.core.mail import send_mail
from django.conf import settings 
from django.urls import reverse

def send_password_reset_mail(email,protocol, domain, token):

    link = protocol+"://"+ domain + reverse('accounts:reset-password', kwargs={'token': token})
    subject = "Your password reset link of YOYO's account"
    # message = f"Hello sir/maa'm, click on the link to reset your password http://127.0.0.1:8000/accounts/reset-password/{token}/"
    message = f"Hello sir/maa'm, click on the link to reset your password {link}"
    
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [email,],
        fail_silently=False,
    )
