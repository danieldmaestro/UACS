from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils.text import slugify

from accounts.models import User
from base.constants import (INTERN, ANALYST, HEAD, MANAGER, MANAGING_DIRECTOR, VP,
                             ASSOCIATE, UPDATED, CREATED, RESET, REVOKED, SUCCESS, ACTION_STATUS,
                             LOGIN, LOGOUT)
from base.models import BaseModel, BaseActivityLog
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.

class Tribe(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name


class Squad(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name


class Designation(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class StaffBaseModel(BaseModel):

    ROLE_CHOICES = (
        (INTERN, INTERN),
        (ASSOCIATE, ASSOCIATE),
        (VP, VP),
        (ANALYST, ANALYST),
        (MANAGER, MANAGER),
        (HEAD, HEAD),
        (MANAGING_DIRECTOR, MANAGING_DIRECTOR),
    )

    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_number = PhoneNumberField()
    tribe = models.ForeignKey(Tribe, on_delete=models.CASCADE)
    squad = models.ForeignKey(Squad, on_delete=models.CASCADE)
    designation = models.ForeignKey(Designation, on_delete=models.CASCADE, null=True)
    role = models.CharField(max_length=100, choices=ROLE_CHOICES, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    class Meta:
        abstract = True

    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Staff(StaffBaseModel):
    email = models.EmailField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.full_name()
    

class Admin(StaffBaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="admin")

    def __str__(self) -> str:
        return self.full_name()


class ServiceProvider(BaseModel):
    name = models.CharField(max_length=150)
    picture = models.ImageField(upload_to='sp_picture/', blank=True, null=True)
    website_url = models.URLField()
    slug = models.SlugField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_date']

    def __str__(self) -> str:
        return self.name


class StaffPermission(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.SET_NULL, related_name="sp_permissions", null=True)
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.SET_NULL, related_name="staff_permissions", null=True)
    is_permitted = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.service_provider.name}({self.staff.first_name})"


ACTION_CHOICES = (
        (UPDATED, UPDATED),
        (RESET, RESET),
        (REVOKED, REVOKED),
        (CREATED, CREATED),
        (LOGIN, LOGIN),
        (LOGOUT, LOGOUT),
    )


class ActivityLog(models.Model):
    actor = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    action_type = models.CharField(choices=ACTION_CHOICES, max_length=15)
    action_time = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)
    status = models.CharField(choices=ACTION_STATUS, max_length=7, default=SUCCESS)
    data = models.JSONField(default=dict)

    # for generic relations
    content_type = models.ForeignKey(
        ContentType, models.SET_NULL, blank=True, null=True
    )
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey()

    class Meta:
        ordering = ['-action_time'] 

    def __str__(self) -> str:
        return f"{self.action_type} by {self.actor} on {self.action_time}"

    def get_activity(self):
        if self.action_type == UPDATED:
            return f"{self.action_type} {self.content_object.staff.full_name()}'s permission for {self.content_object.service_provider.name}"
        elif self.action_type == REVOKED:
            return f"{self.action_type} access for {self.content_object.full_name()}"
        elif self.action_type == RESET:
            return f"{self.action_type} access for {self.content_object.full_name()}"
        elif self.action_type == CREATED:
            return f"{self.action_type} a service provider"

    
    

# class StaffActivityLog(BaseActivityLog):

#     ACTION_CHOICES = (
#         (UPDATED, UPDATED),
#         (RESET, RESET),
#         (REVOKED, REVOKED),
#         (CREATED, CREATED),
#     )

#     action = models.CharField(max_length=20, choices=ACTION_CHOICES)
#     permission = models.ForeignKey(StaffPermission, on_delete=models.SET_NULL, null=True, related_name="staff_activity")

#     def get_activity(self):
#         if self.action == UPDATED:

#         elif self.action == REVOKED:
#             return f"{self.action} access for {self.permission.staff.full_name()}"
#         return f"{self.action} access for {self.permission.staff.full_name()}"
    
# class ServiceProviderActivityLog(BaseActivityLog):

#     ACTION_CHOICES = (
#         (UPDATED, UPDATED),
#         (CREATED, CREATED),
#     )

#     action = models.CharField(max_length=20, choices=ACTION_CHOICES)
#     service_provider = models.CharField(max_length=100)

#     def get_activity(self):
#         return f"{self.action} a service provider, {self.service_provider}"

    
@receiver(pre_save, sender=ServiceProvider)
def slugify_name(sender, instance, **kwargs):
    instance.slug = slugify(instance.name)

