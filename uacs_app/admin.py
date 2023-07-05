from django.contrib import admin
from .models import Staff, ServiceProvider, StaffPermission, StaffActivityLog, ServiceProviderActivityLog

# Register your models here.
admin.site.register(Staff)
admin.site.register(StaffPermission)
admin.site.register(ServiceProvider)
admin.site.register(StaffActivityLog)
admin.site.register(ServiceProviderActivityLog)
