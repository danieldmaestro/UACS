from django.contrib import admin
from .models import Staff, Admin, ServiceProvider, StaffPermission, ActivityLog, Tribe, Squad, Designation

# Register your models here.
admin.site.register(Staff)
admin.site.register(Admin)
admin.site.register(StaffPermission)
admin.site.register(ServiceProvider)
admin.site.register(ActivityLog)
admin.site.register(Tribe)
admin.site.register(Squad)
admin.site.register(Designation)

