import pytest
from django.urls import reverse
from django.test import Client
from accounts.models import User
from bboard.forms import ReviewForm
from bboard.utils import transliterate
from bboard.models import Product
from .. import services
from ..models import Category


@pytest.mark.django_db
def test_home_view_get_request():
    client = Client()

    response = client.get(reverse("home"))

    assert response.status_code == 200


@pytest.mark.django_db
def test_review_form():
    post_data = {
        'reviewer_name': 'TestUser',
        'content': 'Contentmustbemorethan10symbols',
    }
    form = ReviewForm(data=post_data)
    assert form.is_valid()


@pytest.mark.django_db
def test_get_recent_products_with_users():
    category1 = Category.objects.create(name='Category 1', slug=transliterate("Category 1"))
    category2 = Category.objects.create(name='Category 2', slug=transliterate("Category 2"))
    # Создайте пользователей
    user1 = User.objects.create(username='user1', password='password1')
    user2 = User.objects.create(username='user2', password='password2')

    # Создайте продукты, связанные с пользователями
    product1 = Product.objects.create(
        user=user1,
        category=category1,
        title='Product 1',
        price=10.0,
        slug=transliterate('Product 1')
    )
    product2 = Product.objects.create(
        user=user2,
        category=category1,
        title='Product 2',
        price=20.0,
        slug=transliterate('Product 2')
    )
    product3 = Product.objects.create(
        user=user1,
        category=category2,
        title='Product 3',
        price=15.0,
        slug=transliterate('Product 3')
    )
    product4 = Product.objects.create(
        user=user1,
        category=category2,
        title='Product 4',
        price=15.0,
        slug=transliterate('Product 4')
    )
    product5 = Product.objects.create(
        user=user1,
        category=category2,
        title='Product 5',
        price=15.0,
        slug=transliterate('Product 5')
    )

    product6 = Product.objects.create(
        user=user1,
        category=category2,
        title='Product 6',
        price=15.0,
        slug=transliterate('Product 6')
    )

    # Вызов функции для проверки
    recent_products = services.get_recent_products_with_users()

    assert len(recent_products) == 5







