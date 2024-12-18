from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Extra Fields', {'fields': ('bio', 'role')}),
    )
    list_display = ('username', 'email', 'role', 'is_staff', 'is_superuser')


admin.site.register(User, CustomUserAdmin)
