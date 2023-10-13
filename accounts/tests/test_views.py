import pytest
from django.urls import reverse
from accounts.forms import RegistrationForm
from ..models import User
from django.test import Client


