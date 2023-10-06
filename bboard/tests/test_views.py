from django.urls import reverse

from bboard.forms import ReviewForm
from django.test import TestCase


class HomeViewTest(TestCase):
    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/new/index.html')
        self.assertIsInstance(response.context['form'], ReviewForm)