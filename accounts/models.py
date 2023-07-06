from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from base.managers import MyUserManager

# Create your models here.

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True, verbose_name="email address")
    is_staff = models.BooleanField(default=False)


    REQUIRED_FIELDS= []
    USERNAME_FIELD = "email"

    objects = MyUserManager()

    def __str__(self):
        return self.email
 
    







    


