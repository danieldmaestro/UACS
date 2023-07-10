from django.db import models

from accounts.models import User
from base.constants import (UPDATED, CREATED, RESET, REVOKED, SUCCESS, ACTION_STATUS,
                             LOGIN, LOGOUT)


ACTION_CHOICES = (
        (UPDATED, UPDATED),
        (RESET, RESET),
        (REVOKED, REVOKED),
        (CREATED, CREATED),
        (LOGIN, LOGIN),
        (LOGOUT, LOGOUT),
    )


class BaseModel(models.Model):
    created_date = models.DateTimeField(auto_now=True)
    updated_date = models.DateTimeField(auto_now_add=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True
        ordering = ['-created_date']

    
class BaseLog(models.Model):
    actor = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    action_type = models.CharField(choices=ACTION_CHOICES, null=True, blank=True) 
    status = models.CharField(choices=ACTION_STATUS, max_length=7, default=SUCCESS)
    action_time = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)


    class Meta:
        abstract = True


