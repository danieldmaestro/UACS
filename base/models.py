from django.db import models


class BaseModel(models.Model):
    created_date = models.DateTimeField(auto_now=True)
    updated_date = models.DateTimeField(auto_now_add=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True
        ordering = ['-created_date']

    
class BaseActivityLog(models.Model):

    date = models.DateField(auto_now=True)
    time = models.TimeField(auto_now=True)
    actor = models.CharField(max_length=100)

    class Meta:
        abstract = True


