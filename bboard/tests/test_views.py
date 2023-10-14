import pytest
from django.urls import reverse
from django.test import Client, RequestFactory
from accounts.models import User
from bboard.forms import ReviewForm
from bboard.utils import transliterate
from bboard.models import Product
from .. import services
from ..models import Category
from ..models import Review
from ..views import delete_review


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
    # Create categories
    category1 = Category.objects.create(name='Category 1', slug=transliterate("Category 1"))
    category2 = Category.objects.create(name='Category 2', slug=transliterate("Category 2"))

    # Create users
    user1 = User.objects.create_user(username='user1', password='password1')
    user2 = User.objects.create_user(username='user2', password='password2')

    # Create products
    products = [
        Product(user=user1, category=category1, title='Product 1', price=10.0, slug=transliterate('Product 1')),
        Product(user=user2, category=category1, title='Product 2', price=20.0, slug=transliterate('Product 2')),
        Product(user=user1, category=category2, title='Product 3', price=15.0, slug=transliterate('Product 3')),
        Product(user=user1, category=category2, title='Product 4', price=15.0, slug=transliterate('Product 4')),
        Product(user=user1, category=category2, title='Product 5', price=15.0, slug=transliterate('Product 5')),
        Product(user=user1, category=category2, title='Product 6', price=15.0, slug=transliterate('Product 6')),
    ]

    # Save products
    Product.objects.bulk_create(products)

    # Call the function to check
    recent_products = services.get_recent_products_with_users()

    # Assert the result
    assert len(recent_products) == 5


@pytest.mark.django_db
def test_get_recent_reviews_with_reviewers():
    # Create users
    user1 = User.objects.create_user(username='user1', password='password1')
    user2 = User.objects.create_user(username='user2', password='password2')
    user3 = User.objects.create_user(username='user3', password='password3')
    user4 = User.objects.create_user(username='user4', password='password4')
    user5 = User.objects.create_user(username='user5', password='password5')
    user6 = User.objects.create_user(username='user6', password='password6')
    user7 = User.objects.create_user(username='user7', password='password7')
    user8 = User.objects.create_user(username='user8', password='password8')
    user9 = User.objects.create_user(username='user9', password='password9')
    user10 = User.objects.create_user(username='user10', password='password10')
    user11 = User.objects.create_user(username='user11', password='password11')

    reviews = [
        Review(reviewer_name=user1, content="Comment 1"),
        Review(reviewer_name=user2, content="Comment 2"),
        Review(reviewer_name=user3, content="Comment 3"),
        Review(reviewer_name=user4, content="Comment 4"),
        Review(reviewer_name=user5, content="Comment 5"),
        Review(reviewer_name=user6, content="Comment 6"),
        Review(reviewer_name=user7, content="Comment 7"),
        Review(reviewer_name=user8, content="Comment 8"),
        Review(reviewer_name=user9, content="Comment 9"),
        Review(reviewer_name=user10, content="Comment 10"),
        Review(reviewer_name=user11, content="Comment 11"),
    ]

    Review.objects.bulk_create(reviews)

    recent_reviews = services.get_recent_reviews_with_reviewers()
    assert len(recent_reviews) == 10


@pytest.mark.django_db
def test_delete_review_superuser():
    user1 = User.objects.create_user(username='user1', password='password1', is_superuser=True)
    user2 = User.objects.create_user(username="user 2", password="password 2")
    review = Review.objects.create(reviewer_name=user2, content="Comment")

    request = RequestFactory().get(f'/delete-review/{review.id}/')  # Replace with your actual URL
    request.user = user1
    response = delete_review(request, review.id)

    assert response.status_code == 302  # Should redirect




