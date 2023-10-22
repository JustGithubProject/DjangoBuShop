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
from ..forms import ProductForm
from ..models import Category
from ..models import Chat
from ..models import Message
from ..models import Review
from ..views import chat_view
from ..views import create_chat_view
from ..views import create_order
from ..views import create_product
from ..views import delete_chat
from ..views import delete_review
from ..views import get_document_tracking
from ..views import get_products
from ..views import orders_of_user
from ..views import package_search
from ..views import product_detail_view
from ..views import rate_user
from ..views import search_view
from ..views import seller_messages
from ..views import subscribe
from ..views import top_rated_users
from ..views import user_buy
from ..views import user_sell


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


@pytest.mark.django_db
def test_seller_messages():
    user1 = User.objects.create_user(username="testuser1", password="testpassword1")
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
    factory = RequestFactory()
    request = factory.get(reverse("seller_messages", args=[product.slug]))
    request.user = user2

    response = seller_messages(request, product.slug)

    assert response.status_code == 200


@pytest.mark.django_db
def test_user_buy():
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
    Chat.objects.create(
        sender=product.user,
        receiver=user2,
        product=product,
    )
    factory = RequestFactory()
    request = factory.get(reverse("user_buy"))
    request.user = user1
    response = user_buy(request)

    assert response.status_code == 200


@pytest.mark.django_db
def test_user_sell():
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
    Chat.objects.create(
        sender=product.user,
        receiver=user2,
        product=product,
    )
    factory = RequestFactory()
    request = factory.get(reverse("user_sell"))
    request.user = user1
    response = user_sell(request)

    chats = services.get_user_chats(request.user, chat_type="sell")
    assert chats is not None
    assert response.status_code == 200


@pytest.mark.django_db
def test_create_product_get():
    user1 = User.objects.create_user(username="testuser", password="testpassword")
    factory = RequestFactory()
    request = factory.get(reverse("create_product"))
    request.user = user1
    response = create_product(request)
    assert response.status_code == 200


@pytest.mark.django_db
def test_create_product_post():
    user1 = User.objects.create_user(username="testuser", password="testpassword")

    category = Category.objects.create(
        name='Category 2',
        slug=transliterate("Category 2")
    )

    form_data = {
        'user': user1,
        'category': category,
        'title': "Product",
        'description': "Product dec",
        'price': 20.2,
        'slug': transliterate("Product"),
        "image_1": "image_1/image_1.png",
        "image_2": "image_2/image_2.png",
        "image_3": "image_3/image_3.png",
    }
    factory = RequestFactory()
    form = ProductForm(data=form_data)
    assert form.is_valid()


@pytest.mark.django_db
def test_create_order():
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
    factory = RequestFactory()
    request = factory.get(reverse("create_order", args=[product.id]))
    request.user = user2
    response = create_order(request, product.id)
    assert response.status_code == 200

    factory = RequestFactory()
    form_data = {
        "product": product,
        "customer_name": user2,
        "name": "TestName",
        "surname": "TestSurname",
        "city": "New York",
        "department": "something1255",
        "phone_number": "38056727145",
        "email": "Test@gmail.com"
    }
    request = factory.post(reverse("create_order", args=[product.id]), data=form_data)
    request.user = user2
    response = create_order(request, product.id)
    assert response.status_code == 302


@pytest.mark.django_db
def test_orders_of_user():
    user1 = User.objects.create_user(username="testuser", password="testpassword")
    factory = RequestFactory()
    request = factory.get(reverse('orders_of_user'))
    request.user = user1

    response = orders_of_user(request)
    assert response.status_code == 200


@pytest.mark.django_db
def test_delete_chat():
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
    chat1 = Chat.objects.create(
        sender=product.user,
        receiver=user2,
        product=product,
    )

    factory = RequestFactory()
    request = factory.get(reverse('delete_chat', args=[chat1.id]))
    request.user = user2
    response = delete_chat(request, chat1.id)

    assert response.status_code == 302


@pytest.mark.django_db
def test_get_document_tracking_success():
    factory = RequestFactory()
    request = factory.get(reverse('get_document_tracking', args=['20400343432012']))

    response = get_document_tracking(request, '20400343432012')

    assert response.status_code == 200


@pytest.mark.django_db
def test_get_document_tracking_not_found():
    factory = RequestFactory()
    request = factory.get(reverse('get_document_tracking', args=['124441']))

    response = get_document_tracking(request, '3131')

    assert response.status_code == 404


@pytest.mark.django_db
def test_package_search():
    factory = RequestFactory()
    url = reverse("package_search")
    data = {'package_number': '20400343432012'}

    request = factory.get(url, data)

    response = package_search(request)

    assert response.status_code == 302
    assert response.url == reverse('get_document_tracking', args=['20400343432012'])


@pytest.mark.django_db
def test_top_rated_users():
    user1 = User.objects.create_user(username="testuser", password="testpassword", average_rating=5.0)
    user2 = User.objects.create_user(username="testuser2", password="testpassword", average_rating=5.0)

    factory = RequestFactory()
    url = reverse('top_rated_users')
    request = factory.get(url)
    response = top_rated_users(request)

    users = services.get_users_with_high_ratings()
    assert response.status_code == 200
    assert len(users) == 2


@pytest.mark.django_db
def test_subscribe_get():
    factory = RequestFactory()
    request = factory.get(reverse("subscribe"))
    response = subscribe(request)
    assert response.status_code == 200


@pytest.mark.django_db
def test_subscribe_post():
    factory = RequestFactory()
    data = {
        "email": "euqurqu@gmail.com"
    }
    request = factory.post(reverse("subscribe"), data=data)

    response = subscribe(request)
    assert response.status_code == 302
    assert response.url == reverse("home")









