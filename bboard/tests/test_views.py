from django.urls import reverse

from accounts.models import User
from bboard.forms import ReviewForm
from django.test import TestCase

from bboard.models import Product


class HomeViewTest(TestCase):
    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/new/index.html')
        self.assertIsInstance(response.context['form'], ReviewForm)


class SearchViewTest(TestCase):
    def test_search_with_query(self):
        response = self.client.get(reverse("search"), {"query": "Тестовый"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["query"], "Тестовый")
        self.assertTemplateUsed(response, 'products/search_results.html')


class GetProductViewTest(TestCase):
    def test_get_products(self):
        response = self.client.get(reverse("get_products"), {"category": "1", "page": "1"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "products/new/product.html")


