from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from .managers import UserManager
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken
from phonenumber_field.modelfields import PhoneNumberField 
import datetime
import random

def profile_pics_upload_path(instance, filename):
    # Upload to "citizen_id/username/front" or "citizen_id/username/back"
    return f'profile_pics/{instance.phone_number}/{filename}'

class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=30, null=True, default="")
    last_name = models.CharField(max_length=30, null=True, default="")
    phone_number = PhoneNumberField(unique=True, blank=False)  
    profile_pic = models.ImageField(default='default1.jpg', null=True, blank=True, upload_to=profile_pics_upload_path)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'phone_number'  

    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()

    def __str__(self):
        return str(self.phone_number)

    @property
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        
        return {
            'refresh':str(refresh),
            'access':str(refresh.access_token)
        }




class Code(models.Model):
    number = models.CharField(max_length=5, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.number)
    
    def save(self, *args, **kwargs):
        number_list = [x for x in range(10)] 
        code_items = []

        for i in range(5):
            num = random.choice(number_list)
            code_items.append(num)

        code_string = "".join(str(item) for item in code_items)
        self.number = code_string
        super().save(*args, **kwargs)
