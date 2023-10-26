import pytest
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from accounts.forms import RegistrationForm
from ..models import User
from django.test import RequestFactory
from django.test import Client
from ..views import login_view
from ..views import registration_view


@pytest.mark.django_db
def test_registration_view_get():
    user1 = User.objects.create_user(username="testuser", password="testpassword")
    factory = RequestFactory()
    request = factory.get(reverse("register"))

    response = registration_view(request)
    assert response.status_code == 200


@pytest.mark.django_db
def test_registration_view_post():
    client = Client()
    form_data = {
        'username': 'testuser',
        'password1': 'testpassword',
        'password2': 'testpassword',
        'email': 'testuser@example.com',
        'phone_number': '1234567890',
        'city': 'Test City',
        # Add the ReCaptcha field data here if needed
    }
    response = client.post(reverse('register'), data=form_data)
    assert response.status_code == 200


@pytest.mark.django_db
def test_login_view_get():
    factory = RequestFactory()
    request = factory.get(reverse('login'))

    response = login_view(request)

    assert response.status_code == 200


@pytest.mark.django_db
def test_test_login_view_post():
    user1 = User.objects.create_user(username="testuser", password="testpassword")
    client = Client()
    form_data = {
        'username': user1.username,
        'password': 'testpassword'
    }
    response = client.post(reverse('login'), data=form_data)
    assert response.status_code == 302

@pytest.mark.django_db
def test_logout_view():
    # Create a user and log them in
    user = User.objects.create_user(username="testuser", password="testpassword")
    client = Client()
    client.login(username="testuser", password="testpassword")

    # Send a GET request to the logout view
    response = client.get(reverse('logout'))

    # Check if the user is logged out and if they are redirected to the login page
    assert response.status_code == 302  # 302 is the status code for a redirect
    assert response.url == reverse('login')


@pytest.mark.django_db
def test_profile_view():
    # Create a user and log them in
    user = User.objects.create_user(username="testuser", password="testpassword")
    client = Client()
    client.login(username="testuser", password="testpassword")

    # Send a GET request to the profile view
    response = client.get(reverse('profile'))

    # Check if the response status code is 200 (OK)
    assert response.status_code == 200


@pytest.mark.django_db
def test_password_reset_views():
    client = Client()

    # Test the password reset form view
    response = client.get(reverse('password_reset'))
    assert response.status_code == 200  # Check if the form is accessible

    # Simulate a password reset request
    form_data = {
        'email': 'testuser@example.com',  # Replace with a valid email address
    }
    response = client.post(reverse('password_reset'), data=form_data)
    assert response.status_code == 302  # Check if the form submission results in a redirect

    # Test the password reset confirm view
    user = User.objects.create_user(username="testuser", password="testpassword")
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    response = client.get(reverse('password_reset_confirm', args=[uidb64, token]))
    assert response.status_code == 200  # Check if a valid UID and token results in access to the reset confirm form

    # Simulate a password reset confirmation request
    form_data = {
        'new_password1': 'new_password',
        'new_password2': 'new_password',
    }
    response = client.post(reverse('password_reset_confirm', args=[uidb64, token]), data=form_data)
    assert response.status_code == 302  # Check if the password is successfully reset, and the user is redirected to the login page

    # Test the password reset done view
    response = client.get(reverse('password_reset_done'))
    assert response.status_code == 200

