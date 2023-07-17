from django.db import models
from django.contrib.auth.models import AbstractUser
from .utils import CITY_CHOICES


class User(AbstractUser):
    phone_number = models.CharField(max_length=20)
    city = models.CharField(max_length=100, choices=CITY_CHOICES)


