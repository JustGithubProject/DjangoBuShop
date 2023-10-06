from django.test import TestCase
from django.urls import reverse

from ..forms import RegistrationForm
from ..forms import LoginForm


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


class LogoutViewTestCase(TestCase):
    def setUp(self):
        self.username = "testuser"
        self.password = "testpassword"

    def test_logout_view(self):
        response = self.client.get(reverse("logout"))
        self.assertRedirects(response, reverse("login"))


class ProfileViewTestCase(TestCase):
    def test_profile_view_get(self):
        self.client.login(username="username", password="password")

        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/profile.html")


class PasswordResetViewsTest(TestCase):
    def test_password_reset_view(self):
        response = self.client.get(reverse('password_reset'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/password_reset_form.html')

        response = self.client.post(reverse('password_reset'), {'email': "Kropivadanil@gmail.com"})
        self.assertEqual(response.status_code, 302)  # Ожидаем редирект
        # Добавьте проверку отправки письма сброса пароля, если это требуется

    def test_password_reset_done_view(self):
        response = self.client.get(reverse('password_reset_done'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/password_reset_done.html')