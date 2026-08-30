from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

class UserRole(models.TextChoices):
    CLIENT = 'Client', 'CLIENT'
    MECHANIC = 'MECHANIC', 'Mechanic'
    SERVICE_OWNER = 'SERVICE OWNER', 'Service Owner'


class User(AbstractUser):
    role = models.CharField(
        max_length = 255,
        choices = UserRole.choices,
        default = UserRole.CLIENT
    )

    phone_number = models.CharField(
        max_length = 30,
        unique = True,
        null = True,
        blank = True
    )

    avatar = models.ImageField(
        upload_to = 'users/avatars',
        null = True,
        blank = True
    )

    def __str__(self):
        return self.username