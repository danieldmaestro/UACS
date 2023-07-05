from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify


from base.models import StaffBaseModel, BaseModel, BaseActivityLog
from base import constants

# Create your models here.

class Staff(StaffBaseModel):
    email = models.EmailField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.full_name()


class ServiceProvider(BaseModel):
    name = models.CharField(max_length=150)
    picture = models.ImageField(upload_to='accounts/media', blank=True)
    website_url = models.URLField()
    slug = models.SlugField(null=True)

    def __str__(self) -> str:
        return self.name


class StaffPermission(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.SET_NULL, related_name="sp_permissions", null=True)
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.SET_NULL, related_name="staff_permissions", null=True)
    is_permitted = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.service_provider.name}({self.staff.first_name})"
    

class StaffActivityLog(BaseActivityLog):

    ACTION_CHOICES = (
        (constants.UPDATED, "Updated"),
        (constants.CREATED, "Created"),
        (constants.RESET, "Restored"),

    )

    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    permission = models.ForeignKey(StaffPermission, on_delete=models.SET_NULL, null=True, related_name="staff_activity")

    def get_activity(self):
        if self.action == "Updated":
            return f"{self.action} {self.permission.staff.full_name()}'s permission for {self.permission.service_provider.name}"
        elif self.action == "Revoked":
            return f"{self.action} access for {self.permission.staff.full_name()}"
        return f"{self.action} access for {self.permission.staff.full_name()}"
    
class ServiceProviderActivityLog(BaseActivityLog):

    ACTION_CHOICES = (
        (constants.UPDATED, "Updated"),
        (constants.CREATED, "Created"),
    )

    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    service_provider = models.CharField(max_length=100)

    def get_activity(self):
        return f"{self.action} a service provider, {self.service_provider}"

    
@receiver(pre_save, sender=ServiceProvider)
def slugify_name(sender, instance, **kwargs):
    instance.slug = slugify(instance.name)
