import pytest
from django.urls import reverse
from accounts.forms import RegistrationForm
from ..models import User
from django.test import Client


@pytest.mark.django_db
def test_registration_view_post_success():
    client = Client()
    user_data = {
        "username": "test_user",
        "password1": "mCHhKe7rYKnuc",
        "password2": "mCHhKe7rYKnuc",
        "email": "test_user@example.com",
        "phone_number": "+1234567890",
        "city": "Test City",
    }
    response = client.post(reverse("register"), user_data)
    print(response.content)
    assert response.status_code == 200
    assert User.objects.filter(username="test_user").exists()

    # Clean up the test data
    User.objects.filter(username="test_user").delete()


@pytest.mark.django_db
def test_registration_view_get():
    client = Client()
    response = client.get(reverse("register"))
    assert response.status_code == 200  # Ожидается успешный ответ

    # Проверка, что форма отображается на странице
    assert isinstance(response.context["form"], RegistrationForm)
