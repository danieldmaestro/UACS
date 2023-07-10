from django.contrib import admin
from .models import Staff, Admin, ServiceProvider, StaffPermission, ActivityLog, Tribe, Squad, Designation, SecurityLog
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


# Register your models here.

class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['actor', 'action_time', 'action_type', 'status']


class SecurityLogAdmin(admin.ModelAdmin):
    list_display = ['actor', 'action_time', 'action_type', 'status']

admin.site.register(Staff)
admin.site.register(Admin)
admin.site.register(StaffPermission)
admin.site.register(ServiceProvider)
admin.site.register(ActivityLog, ActivityLogAdmin)
admin.site.register(SecurityLog, SecurityLogAdmin)
admin.site.register(Tribe)
admin.site.register(Squad)
admin.site.register(Designation)

