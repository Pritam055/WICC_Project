from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser,Certificate

# Register your models here.

class CustomUserAdmin(UserAdmin):

    def group(self, user):
        groups = []
        for group in user.groups.all():
            groups.append(group.name)
        return ' '.join(groups)
    group.short_description = 'Groups'

    list_display = ('username','id', 'email', 'user_type', 'group', 'verified')
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
                )
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
        ('Additional info', {   
            'fields': ('address', 'phone', 'user_type', 'verified', 'forget_password_token')
        })
    )

admin.site.register(CustomUser, CustomUserAdmin)

admin.site.register(Certificate)