from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class BaseModel(models.Model):
    created_date = models.DateTimeField(auto_now=True)
    updated_date = models.DateTimeField(auto_now_add=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True
        ordering = ['-created_date']

class StaffBaseModel(BaseModel):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_number = PhoneNumberField()
    tribe = models.CharField(max_length=100)
    squad = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)

    class Meta:
        abstract = True

    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    

class BaseActivityLog(models.Model):

    date = models.DateField(auto_now=True)
    time = models.TimeField(auto_now=True)
    actor = models.CharField(max_length=100)

    class Meta:
        abstract = True


