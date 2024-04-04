from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):

    def create_user(self, first_name, last_name, phone_number, password=None,**extra_fields):
        if not first_name:
            raise ValueError(_("First name is required"))
        if not last_name:
            ValueError(_("Last name is required"))
        if not phone_number:
                raise ValueError('The phone number must be set')
        user = self.model(first_name=first_name, last_name=last_name, phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, phone_number, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)  # Corrected field name to "is_staff"
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("is_staff must be True for admin user"))

        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("is_superuser must be True for admin user"))

        user = self.create_user(first_name, last_name, phone_number, password, **extra_fields)
        return user
