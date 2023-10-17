import pytest
from django.http import HttpResponse
from django.urls import reverse
from django.test import Client
from django.test import RequestFactory

from accounts.models import User
from bboard.forms import ReviewForm
from bboard.utils import transliterate
from bboard.models import Product
from .. import services
from ..models import Category
from ..models import Chat
from ..models import Message
from ..models import Review
from ..views import chat_view
from ..views import create_chat_view
from ..views import delete_review
from ..views import get_products
from ..views import product_detail_view
from ..views import search_view


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


@pytest.mark.django_db
def test_search_view():
    user = User.objects.create_user(
        username="testuser",
        password="password1"
    )
    category = Category.objects.create(
        name='Category 2',
        slug=transliterate("Category 2")
    )
    product = Product.objects.create(
        user=user,
        category=category,
        title="Product",
        description="Product dec",
        price=20.2,
        slug=transliterate("Product")
    )

    factory = RequestFactory()
    request = factory.get(f"/search/?query={product.title}")

    response = search_view(request)
    assert response.status_code == 200
    assert product.title in str(response.content)
    assert product.description in str(response.content)

    request = factory.get("/search/?query=")

    response = search_view(request)

    assert response.status_code == 200

    product.delete()


@pytest.mark.django_db
def test_get_products():
    factory = RequestFactory()
    request = factory.get("/get-products-from-inventory/")

    response = get_products(request)

    assert response.status_code == 200


@pytest.mark.django_db
def test_product_detail_view():
    user = User.objects.create_user(
        username="testuser",
        password="password1"
    )
    category = Category.objects.create(
        name='Category 2',
        slug=transliterate("Category 2")
    )
    product = Product.objects.create(
        user=user,
        category=category,
        title="Product",
        description="Product dec",
        price=20.2,
        slug=transliterate("Product")
    )
    factory = RequestFactory()
    request = factory.get(f"/product/{product.slug}")
    response = product_detail_view(request, product.slug)
    assert response.status_code == 200


@pytest.mark.django_db
def test_create_chat_view_authenticated_user():
    user = User.objects.create_user(
        username="testuser",
        password="password1"
    )
    category = Category.objects.create(
        name='Category 2',
        slug=transliterate("Category 2")
    )
    product = Product.objects.create(
        user=user,
        category=category,
        title="Product",
        description="Product dec",
        price=20.2,
        slug=transliterate("Product")
    )

    # Создаем фейковый запрос
    factory = RequestFactory()
    url = reverse('create_chat', args=[product.slug])
    request = factory.get(url)
    request.user = user

    # Вызываем представление
    response = create_chat_view(request, slug=product.slug)

    # Проверяем, что статус ответа равен 302 (ожидаем перенаправление)
    assert response.status_code == 302

    # Проверяем, что чат был создан
    chat = services.create_or_get_chat(user, product)
    assert chat is not None

    # Проверяем, что пользователь перенаправлен в чат
    assert response.url == reverse('chat', args=[chat.id])


@pytest.mark.django_db
def test_chat_view_access():
    # Создаем экземпляр фабрики запросов
    factory = RequestFactory()

    # Создаем тестового пользователя и авторизуем его
    user1 = User.objects.create_user(username="testuser", password="testpassword")
    user2 = User.objects.create_user(username="testuser2", password="testpassword2")
    user3 = User.objects.create_user(username="testuser3", password="testpassword3")

    category = Category.objects.create(
        name='Category 2',
        slug=transliterate("Category 2")
    )
    product = Product.objects.create(
        user=user1,
        category=category,
        title="Product",
        description="Product dec",
        price=20.2,
        slug=transliterate("Product")
    )
    chat = Chat.objects.create(
        sender=product.user,
        receiver=user2,
        product=product,
    )
    request = factory.get(f'/chat/{chat.id}/')  # Замените URL на свой chat_view
    request.user = user2
    # Может потребоваться создать объект chat и messages с помощью services

    # Вызываем представление и получаем HTTP-ответ
    response = chat_view(request, chat_id=chat.id)  # Замените chat_id на существующий чат

    # Проверяем, что представление возвращает HttpResponse с ожидаемым текстом
    assert isinstance(response, HttpResponse)
    print(response.content.decode())
    assert "У вас нет доступа к этому чату." not in response.content.decode()

    # Проверяем статус кода ответа
    assert response.status_code == 200  # Замените на ожидаемый статус код
    factory = RequestFactory()
    request = factory.get(f'/chat/{chat.id}/')
    request.user = user3
    response = chat_view(request, chat_id=chat.id)
    assert "У вас нет доступа к этому чату." in response.content.decode()


@pytest.mark.django_db
def test_get_chat_and_messages():
    # Создаем экземпляр фабрики запросов
    factory = RequestFactory()

    # Создаем тестового пользователя и авторизуем его
    user1 = User.objects.create_user(username="testuser", password="testpassword")
    user2 = User.objects.create_user(username="testuser2", password="testpassword2")

    category = Category.objects.create(
        name='Category 2',
        slug=transliterate("Category 2")
    )
    product = Product.objects.create(
        user=user1,
        category=category,
        title="Product",
        description="Product dec",
        price=20.2,
        slug=transliterate("Product")
    )
    chat = Chat.objects.create(
        sender=product.user,
        receiver=user2,
        product=product,
    )
    Message.objects.create(
        chat=chat,
        sender=user2,
        content="test content"
    )

    chat_, messages_ = services.get_chat_and_messages(user2, chat.id)

    assert chat_ is not None and messages_ is not None


