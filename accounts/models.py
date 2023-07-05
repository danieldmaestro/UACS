from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from base.managers import MyUserManager
from base.models import StaffBaseModel, BaseModel

# Create your models here.

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True, verbose_name="email address")
    is_staff = models.BooleanField(default=False)


    REQUIRED_FIELDS= []
    USERNAME_FIELD = "email"

    objects = MyUserManager()

    def __str__(self):
        return self.email
 
    
class Admin(StaffBaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="admin")

    def __str__(self) -> str:
        return self.full_name()






    


