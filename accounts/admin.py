from django.contrib import admin

# Register your models here.

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
    (
        'Additional Information' , {
        'fields'  : (
            'role',
            'phone_number',
            'avatar'
        )
    },
    ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
    (
        'Additional Information' ,{
        'fields' : (
            'role',
            'phone_number',
            'avatar'
        )
    },
    ),
    )
