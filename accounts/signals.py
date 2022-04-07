from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group

from django.contrib.auth import get_user_model

@receiver(post_save, sender=get_user_model())
def isUserAdminSignal(sender, instance, created, *args, **kwargs):
    if created and instance.is_superuser : 
        instance.groups.add(Group.objects.get(name='admin-gang'))
        instance.save()