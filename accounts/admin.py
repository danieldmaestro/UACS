from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Register your models here.
class UserAdmin(BaseUserAdmin):

    ordering = ('email',)  # Set the ordering field to 'email'
    list_display = ('email', 'is_staff', 'is_active')  # Add 'role', 'is_staff', and 'is_active' to the list_display field
    list_filter = ('is_staff', 'is_superuser',)  # Add 'role' to the list_filter field
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser')}),
        ("Dates", {"fields": ("last_login",)})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2',),
        }),
    )

admin.site.register(User, UserAdmin)
