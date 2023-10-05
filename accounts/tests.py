from django.test import TestCase
from django.urls import reverse
from .forms import RegistrationForm, LoginForm


class RegistrationViewTest(TestCase):
    def test_registration_view_get(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["form"], RegistrationForm)
        self.assertTemplateUsed(response, "users/registration.html")

    def test_registration_view_post_valid_data(self):
        data = {
            'username': 'testuser',
            'password1': 'testpassword',
            'password2': 'testpassword',
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 200)


class LoginViewTest(TestCase):
    def setUp(self):
        self.username = "testuser"
        self.password = "testpassword"

    def test_login_get(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["form"], LoginForm)
        self.assertTemplateUsed(response, "users/login.html")

    def test_login_view_post_valid_credentials(self):
        data = {
            "username": self.username,
            "password": self.password
        }
        response = self.client.post(reverse("login"), data)
        self.assertEqual(response.status_code, 200)



