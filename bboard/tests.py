from django.test import TestCase
from django.urls import reverse
from . import services


class HomeViewTest(TestCase):
    def test_home_view_template(self):
        response = self.client.get(reverse("home"))
        self.assertTemplateUsed(response, "products/new/index.html")

    def test_home_view_context(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

        self.assertIn("products", response.context)
        self.assertIn("form", response.context)
        self.assertIn("reviews", response.context)
        self.assertIn("quantity_users", response.context)