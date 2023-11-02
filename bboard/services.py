import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
from django import template
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect

from project import settings
from project.settings import EMAIL_HOST
from project.settings import EMAIL_HOST_PASSWORD
from project.settings import EMAIL_HOST_USER
from project.settings import EMAIL_PORT
from .models import Cart
from .models import CartItem
from .models import Category
from .models import Chat
from .models import Message
from .models import Order
from .models import OrderCart
from .models import Product, Review
from accounts.models import User
from .forms import ReviewForm


####################################################################
#               БИЗНЕС ЛОГИКА ДЛЯ HOME_VIEW                        #
####################################################################
from .utils import transliterate


def get_recent_products_with_users():
    """
    Получение недавно добавленных продуктов с информацией о пользователях, добавивших их.

    :return: QuerySet недавно добавленных продуктов.
    """
    return Product.objects.order_by('-created_at').select_related('user')[:5]


def get_recent_reviews_with_reviewers():
    """
    Получение недавних отзывов с информацией об авторах.

    :return: QuerySet недавних отзывов с информацией об авторах.
    """
    return Review.objects.order_by("date_posted").select_related('reviewer_name')[:10]


def process_review_form(request):
    """
    Обработка формы отзыва.

    :param request: Объект запроса Django.
    :return: True, если форма успешно обработана, иначе False.
    """
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.reviewer_name = request.user
            review.save()
            return True  # Успешно обработано
    return False


def get_user_count():
    """
    Получение общего количества пользователей.

    :return: Количество пользователей.
    """
    return User.objects.count()


####################################################################
#               БИЗНЕС ЛОГИКА  search_view                         #
####################################################################


def search_products(query):
    """
    Поиск продуктов по запросу.

    :param query: Поисковый запрос.
    :return: QuerySet продуктов, соответствующих запросу.
    """
    if not query:
        return None
    return Product.objects.filter(Q(title__icontains=query) | Q(description__icontains=query))


#####################################################################
#               БИЗНЕС ЛОГИКА  get_products                         #
#####################################################################

def get_all_categories():
    """
    Получение всех категорий товаров.

    :return: QuerySet всех категорий.
    """
    return Category.objects.all()


def get_products_by_category(selected_category_id):
    """
    Получение продуктов по выбранной категории.

    :param selected_category_id: Идентификатор выбранной категории.
    :return: QuerySet продуктов, соответствующих выбранной категории.
    """
    if selected_category_id:
        return Product.objects.filter(category__slug=selected_category_id)
    return Product.objects.order_by('-created_at')[:10]


def paginate_products(products, page_number, per_page=9):
    """
    Пагинация списка продуктов.

    :param products: QuerySet продуктов для пагинации.
    :param page_number: Номер страницы для отображения.
    :param per_page: Количество продуктов на странице (по умолчанию 9).
    :return: Объект страницы с продуктами.
    """
    paginator = Paginator(products, per_page)
    return paginator.get_page(page_number)


#####################################################################
#               БИЗНЕС ЛОГИКА  create_chat_view                     #
#####################################################################

def create_or_get_chat(sender, product):
    """
    Создание или получение чата между отправителем и получателем.

    :param sender: Пользователь-отправитель.
    :param product: Продукт-получатель.
    :return: Объект чата.
    """
    chat_exists = Chat.objects.filter(sender=sender, receiver=product.user, product=product).first()

    if chat_exists:
        return chat_exists

    # Если чат не существует, создаем его
    chat = Chat.objects.create(sender=sender, receiver=product.user, product=product)
    return chat

#####################################################################
#               БИЗНЕС ЛОГИКА  chat_view                            #
#####################################################################


def get_chat_and_messages(user, chat_id):
    """
    Получение чата и сообщений для пользователя и чата с указанным ID.

    :param user: Пользователь, который запрашивает чат.
    :param chat_id: Идентификатор чата.
    :return: Объект чата и QuerySet сообщений или None, если пользователь не имеет доступа к чату.
    """
    chat = get_object_or_404(Chat.objects.select_related('receiver'), id=chat_id)

    if user != chat.sender and user != chat.receiver:
        return None, None

    messages = Message.objects.filter(chat=chat).order_by('created_at').select_related('sender')
    return chat, messages


#####################################################################
#               БИЗНЕС ЛОГИКА  send_message_view                    #
#####################################################################

def create_and_save_message(chat, sender, content):
    """
    Создание и сохранение сообщения в чате.

    :param chat: Чат, в который отправляется сообщение.
    :param sender: Пользователь-отправитель.
    :param content: Текст сообщения.
    :return: True, если сообщение успешно создано и сохранено, иначе False.
    """
    try:
        message = Message(chat=chat, sender=sender, content=content)
        message.save()
        return True
    except Exception as e:
        print(f"{e}")
        return False


#####################################################################
#               БИЗНЕС ЛОГИКА  seller_messages                    #
#####################################################################

def get_seller_chats(user, product):
    """
    Получение чатов, где пользователь является продавцом и они связаны с конкретным продуктом.

    :param user: Пользователь-продавец.
    :param product: Продукт, для которого нужны чаты.
    :return: QuerySet чатов.
    """
    return Chat.objects.filter(receiver=user, product=product).select_related('sender', 'product')

#####################################################################
#               БИЗНЕС ЛОГИКА  user_buy  и user_sell                #
#####################################################################


def get_user_chats(user, chat_type):
    """
    Получение чатов пользователя в зависимости от типа (покупка или продажа).

    :param user: Пользователь, для которого нужны чаты.
    :param chat_type: Тип чатов ('buy' или 'sell').
    :return: QuerySet чатов пользователя в зависимости от типа.
    """
    if chat_type == "buy":
        return Chat.objects.filter(sender=user).select_related('receiver', 'product')
    elif chat_type == "sell":
        return Chat.objects.filter(receiver=user).select_related('sender')
    else:
        # Обработка некорректного типа чата (по умолчанию показываем покупки)
        return Chat.objects.filter(sender=user).select_related('receiver', 'product')


#####################################################################
#               БИЗНЕС ЛОГИКА  create_product                       #
#####################################################################

def save_product(request, form):
    """
    Сохранение товара и генерация slug.

    :param request: Объект запроса Django.
    :param form: Форма с данными о товаре.
    """
    product = form.save(commit=False)
    product.user = request.user

    # Generate slug from title and transliterate if necessary
    title = form.cleaned_data['title']
    slug = transliterate(title)
    product.slug = slug

    product.save()


#####################################################################
#               БИЗНЕС ЛОГИКА  create_order                         #
#####################################################################

def save_order(request, form, product):
    """
    Сохранение заказа.

    :param request: Объект запроса Django.
    :param form: Форма с данными о заказе.
    :param product: Продукт, для которого создается заказ.
    """
    order = form.save(commit=False)
    order.customer_name = request.user
    order.product = product
    order.save()


#####################################################################
#               БИЗНЕС ЛОГИКА  orders_of_users                      #
#####################################################################

def get_user_orders(user):
    """
    Получение заказов определенного пользователя.

    :param user: Пользователь, для которого нужны заказы.
    :return: QuerySet заказов пользователя.
    """
    return Order.objects.select_related('product__user').filter(customer_name=user)


def paginate_orders(request, orders, per_page=1):
    """
    Пагинация списка заказов.

    :param request: Объект запроса Django.
    :param orders: QuerySet заказов для пагинации.
    :param per_page: Количество заказов на странице (по умолчанию 1).
    :return: Объект страницы с заказами.
    """
    paginator = Paginator(orders, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


#####################################################################
#               БИЗНЕС ЛОГИКА  top_rated_users                      #
#####################################################################

def get_users_with_high_ratings():
    """
    Получение пользователей с высокими рейтингами.

    :return: QuerySet пользователей с высокими рейтингами (больше 4).
    """
    return User.objects.filter(average_rating__gt=4).order_by('-average_rating')[:10]


def get_user_by_username(username_):
    """
    Получение пользователя по его имени пользователя.

    :param username_: Имя пользователя.
    :return: Объект пользователя.
    """
    return User.objects.get(username=username_)


def fetch_tracking_info(tracking_number):
    """
    Получение информации о трекинге по номеру трекинга.

    :param tracking_number: Номер трекинга.
    :return: Информация о трекинге или None, если данные не найдены.
    """
    api_url = settings.NOVA_POSHTA_API_URL
    payload = {
        "apiKey": settings.NOVA_POSHTA_API_KEY,
        "modelName": "TrackingDocument",
        "calledMethod": "getStatusDocuments",
        "methodProperties": {
            "Documents": [
                {"DocumentNumber": tracking_number}
            ]
        }
    }

    response = requests.post(api_url, json=payload)
    data = response.json()

    if "data" in data and data["data"]:
        tracking_data = data["data"][0]
        return tracking_data
    else:
        return None

#####################################################################
#               БИЗНЕС ЛОГИКА  orders_of_user_from_cart             #
#####################################################################


def get_orders_from_cart(user):
    """
    Получение заказов из корзины для пользователя.

    :param user: Пользователь, для которого нужны заказы из корзины.
    :return: QuerySet заказов из корзины для пользователя.
    """
    return OrderCart.objects.filter(customer_name=user)

#####################################################################
#               БИЗНЕС ЛОГИКА  add_to_cart                          #
#####################################################################


def get_product_by_id(product_id):
    return Product.objects.get(id=product_id)


def get_or_create_cart_by_user(user):
    user_cart, created = Cart.objects.get_or_create(user=user)
    return user_cart, created


def get_or_create_cart_item_by_cart_and_product(cart, product):
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    return cart_item, created

#####################################################################
#               БИЗНЕС ЛОГИКА  subscribe                            #
#####################################################################


def send_subscription_confirmation(email):
    # Настройте параметры SMTP-сервера
    smtp_host = EMAIL_HOST  # Замените на адрес вашего SMTP-сервера
    smtp_port = EMAIL_PORT  # Замените на порт вашего SMTP-сервера
    smtp_username = EMAIL_HOST_USER  # Замените на свое имя пользователя SMTP
    smtp_password = EMAIL_HOST_PASSWORD  # Замените на свой пароль SMTP

    # Создайте сообщение
    subject = 'Subscription Confirmation'
    message = f'Thank you for subscribing! Click the link to visit our website: http://127.0.0.1:8000/'
    from_email = EMAIL_HOST_USER  # Замените на вашу электронную почту

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = email
    msg['Subject'] = subject

    body = message
    msg.attach(MIMEText(body, 'plain'))

    # Отправьте сообщение через SMTP
    try:
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(from_email, email, msg.as_string())
        server.quit()

        return True  # Подписка успешно отправлена

    except Exception as e:
        print(e)
        return False  # Ошибка при отправке подписки


#####################################################################
#               БИЗНЕС ЛОГИКА  create_order_cart                    #
#####################################################################

def create_order_from_cart(user, form):
    cart = Cart.objects.get(user=user)

    if cart.products.exists():
        total_price = sum(product.price for product in cart.products.all())

        # Сначала создайте заказ и сохраните его
        order_cart = form.save(commit=False)
        order_cart.customer_name = user
        order_cart.price = total_price
        order_cart.save()

        # Затем добавьте продукты к заказу
        for product in cart.products.all():
            order_cart.products.add(product)

        # Очистите корзину
        cart.products.clear()

        return True  # Заказ успешно создан

    return False  # Корзина пуста, заказ не создан


def count_messages(msgs, user):
    count = 0
    for message in msgs:
        if not message.is_read and message.sender != user:
            count += 1
            message.is_read = True
            message.save()
    return count


#####################################################################
#               БИЗНЕС ЛОГИКА  get_cart                             #
#####################################################################


def get_cart_by_user(user):
    return Cart.objects.get(user=user)


def create_cart_by_user(user):
    return Cart.objects.create(user=user)


# create express invoice for product NOVA POSHTA
def create_express_invoice_for_product(
        cost,
        datetime,
        weight,
        city_sender,
        sender,
        sender_address,
        contact_sender,
        sender_phone,
        city_recipient,
        recipient,
        recipient_address,
        contact_recipient,
        recipient_phone
    ):
    api_url = f"{settings.NOVA_POSHTA_API_URL}"
    payload = {
        "apiKey": settings.NOVA_POSHTA_API_KEY,
        "modelName": "InternetDocument",
        "calledMethod": "save",
        "methodProperties": {
            "SenderWarehouseIndex": "134",
            "RecipientWarehouseIndex": "168",
            "PayerType": "ThirdPerson",
            "PaymentMethod": "Cash",
            "DateTime": datetime,  # дд.мм.рррр
            "CargoType": "Cargo",
            # Значение "Cargo" обычно означает, что отправляемый груз является грузом, а не письмом или документом.
            "VolumeGeneral": "0.45",
            "Weight": weight,
            "ServiceType": "DoorsWarehouse",
            "SeatsAmount": "2",
            "Description": "Додатковий опис відправлення",
            "Cost": cost,
            "CitySender": city_sender,
            "Sender": sender,
            "SenderAddress": sender_address,
            "ContactSender": contact_sender,
            "SendersPhone": sender_phone,
            "CityRecipient": city_recipient,
            "Recipient": recipient,
            "RecipientAddress": recipient_address,
            "ContactRecipient": contact_recipient,
            "RecipientsPhone": recipient_phone
        }
    }
    response = requests.post(api_url, json=payload)
    data = response.json()
    print(data)
    if "data" in data and data['data']:
        express_invoice = data["data"][0]["Ref"]  # Ідентификатор експрес-накладной
        cost_on_site = data["data"][0]["CostOnSite"]  # Вартість доставки
        estimated_delivery_date = data["data"][0]["EstimatedDeliveryDate"]  # Прогнозована дата доставки
        int_doc_number = data["data"][0]["IntDocNumber"]  # Номер експрес-накладной
        type_document = data["data"][0]["TypeDocument"]  # Тип експрес-накладной
        return express_invoice, cost_on_site, estimated_delivery_date, int_doc_number, type_document

