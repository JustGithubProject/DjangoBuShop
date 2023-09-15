import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.contrib import messages
from django.utils import translation
from django.views.decorators.cache import cache_page

from accounts.models import User
from project import settings
from project.settings import EMAIL_HOST
from project.settings import EMAIL_HOST_PASSWORD
from project.settings import EMAIL_HOST_USER
from project.settings import EMAIL_PORT
from .forms import ReviewForm
from .models import Review

from .utils import transliterate
from .utils import decode_status
from .forms import ProductForm
from .forms import OrderForm
from .models import Chat
from .models import Message
from .models import Order
from .models import Product
from .models import Category
from . import services


def home_view(request):
    """home_view --> Главная страница   """
    products = services.get_recent_products_with_users()
    reviews = services.get_recent_reviews_with_reviewers()

    if services.process_review_form(request):
        return redirect("home")

    form = ReviewForm()

    quantity_users = services.get_user_count()
    return render(request, "products/new/index.html",
                  {"products": products, "form": form, "reviews": reviews, "quantity_users": quantity_users})


def delete_review(request, review_id):
    """delete_review -> удалить  комментарий """
    review = get_object_or_404(Review, id=review_id)

    if request.user.is_superuser:
        review.delete()
        return redirect("home")
    else:
        return HttpResponse("У вас нет прав на удаление этого комментария")


def search_view(request):
    """search_view - Поле поиска """
    query = request.GET.get("query")
    products = services.search_products(query)

    context = {
        'query': query,
        'products': products,
    }
    return render(request, 'products/search_results.html', context)


def get_products(request):
    categories = services.get_all_categories()
    selected_category_id = request.GET.get('category')
    products = services.get_products_by_category(selected_category_id)
    page_number = request.GET.get("page")
    page_obj = services.paginate_products(products, page_number)

    return render(request, 'products/new/product.html',
                  {'categories': categories, 'products': page_obj, 'selected_category_id': selected_category_id})


def product_detail_view(request, slug):
    """
    product_detail_view --> Детально про товар, где можно написать продавцу или продавцу посмотреть сообщения
    """
    product = get_object_or_404(Product.objects.select_related('user'), slug=slug)
    return render(request, 'products/product_detail.html', {'product': product, 'messages': messages})


@login_required
def create_chat_view(request, slug):
    """
    create_chat_view --> обработчик для перехода в чат(если он существует) или создания чата и перехода к нему
    """
    product = get_object_or_404(Product, slug=slug)

    if not request.user.is_authenticated:
        return redirect("login")

    chat = services.create_or_get_chat(request.user, product)

    return redirect("chat", chat_id=chat.id)


@login_required
def chat_view(request, chat_id):
    """
    chat_view --> чат между двумя пользователями
    """
    chat, messages = services.get_chat_and_messages(request.user, chat_id)
    if chat is None:
        return HttpResponse("У вас нет доступа к этому чату.")

    return render(request, "products/chat.html", {"chat": chat, "messages": messages})


@login_required
def send_message_view(request, chat_id):
    """
    send_message_view --> отправка сообщений, и редирект для того, чтобы страница обновилась
    """
    chat = get_object_or_404(Chat, id=chat_id)

    # Проверяем, авторизован ли пользователь
    if not request.user.is_authenticated:
        return redirect('login')  # Перенаправляем на страницу входа, если пользователь не авторизован

    # Проверяем, является ли текущий пользователь участником чата
    if request.user != chat.sender and request.user != chat.receiver:
        return HttpResponseForbidden("У вас нет доступа к этому чату")

    if request.method == 'POST':
        message_content = request.POST.get('message')

        result = services.create_and_save_message(chat, request.user, message_content)
        if result:
            messages.success(request, "Сообщение успешно отправлено")

    return redirect('chat', chat_id=chat_id)


@login_required
def seller_messages(request, slug):
    """
    seller_messages --> продавец может посмотреть тех, кто оправлял ему сообщения
    """
    product = get_object_or_404(Product, slug=slug)

    chats = services.get_seller_chats(request.user, product)
    return render(request, "products/seller_messages.html", {"chats": chats, "product": product})


@login_required
def user_buy(request):
    """
    user_buy --> чаты, где пользователь что-то покупает
    """
    chats = services.get_user_chats(request.user, chat_type="buy")
    return render(request, "products/buy.html", {"chats": chats, "temp": "buy"})


@login_required
def user_sell(request):
    """
    user_sell --> чаты, где пользователь что-то продает
    """
    chats = services.get_user_chats(request.user, chat_type="sell")
    return render(request, "products/sell.html", {"chats": chats, "temp": "sell"})


@login_required
@cache_page(300)
def create_product(request):
    """
    create_product -> view для создания Товара, любой пользователь может добавить свой товар
    """
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            services.save_product(request, form)
            return redirect("home")
        else:
            print(form.errors)
    else:
        form = ProductForm()
    return render(request, 'products/create_product.html', {'form': form})


@login_required
def create_order(request, product_id):
    """
    create_order -> Делает заказ и сохраняет его в бд
    """
    product = get_object_or_404(Product, pk=product_id)

    if request.method == "POST" and request.user != product.user:
        form = OrderForm(request.POST)
        if form.is_valid():
            services.save_order(request, form, product)
            return redirect("home")
        else:
            print(form.errors)
    else:
        form = OrderForm()

    return render(request, "products/create_order.html", {"form": form})



@login_required
def orders_of_user(request):
    """
    orders_of_users -> Все заказы определенного пользователя
    """
    orders = services.get_user_orders(request.user)
    page_obj = services.paginate_orders(request, orders)
    return render(request, "products/orders.html", {"page_obj": page_obj})


def delete_chat(request, chat_id):
    """
    delete_chat -> view для удаления чата, каждый пользователь может удалить свои чаты
    """
    chat = get_object_or_404(Chat, id=chat_id)

    if chat.receiver == request.user or chat.sender == request.user:
        chat.delete()
        return redirect("user_sell")
    else:
        return HttpResponse("У вас нет прав на удаление этого чата.")


###############################################
# Новая Почта
###############################################


def get_document_tracking(request, tracking_number):
    """
    Информация о посылке по накладной
    """
    api_url = f"{settings.NOVA_POSHTA_API_URL}"
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
    ####################################
    # Получение данных из json
    weight = data["data"][0]["DocumentWeight"]
    cost_of_delivery = data["data"][0]["DocumentCost"]
    status_code = data["data"][0]["StatusCode"]
    status_code_decoding = decode_status[str(status_code)]
    number_squad = data["data"][0]["WarehouseRecipientNumber"]
    city_sender = data["data"][0]["CitySender"]
    decoded_city_sender = city_sender.encode().decode()
    city_recipient = data["data"][0]["CityRecipient"]
    decoded_city_recipient = city_recipient.encode().decode()
    ######################################

    context = {
        "weight": weight,
        "cost_of_delivery": cost_of_delivery,
        "status_code_decoding": status_code_decoding,
        "number_squad": number_squad,
        "decoded_city_sender": decoded_city_sender,
        "decoded_city_recipient": decoded_city_recipient
    }

    return render(request, "products/get_document_tracking.html", context=context)


##################################################################################################
#  package_search -> обработчик для формы, которая ищет информацию по декларации новой почты     #
##################################################################################################


def package_search(request):
    declaration = request.GET.get("package_number")
    if declaration:
        return redirect('get_document_tracking', declaration)
    return render(request, "products/package_search.html", {"declaration": declaration})


# def create_express_invoice_for_product(request):
#     api_url = f"{settings.NOVA_POSHTA_API_URL}"
#     payload = {
#         "apiKey": settings.NOVA_POSHTA_API_KEY,
#         "modelName": "InternetDocument",
#         "calledMethod": "save",
#         "methodProperties": {
#             "SenderWarehouseIndex": "101/102",
#             "RecipientWarehouseIndex": "101/102",
#             "PayerType": "ThirdPerson",
#             "PaymentMethod": "NonCash",
#             "DateTime": "дд.мм.рррр",
#             "CargoType": "Cargo",
#             "VolumeGeneral": "0.45",
#             "Weight": "0.5",
#             "ServiceType": "DoorsWarehouse",
#             "SeatsAmount": "2",
#             "Description": "Додатковий опис відправлення",
#             "Cost": "15000",
#             "CitySender": "00000000-0000-0000-0000-000000000000",
#             "Sender": "00000000-0000-0000-0000-000000000000",
#             "SenderAddress": "00000000-0000-0000-0000-000000000000",
#             "ContactSender": "00000000-0000-0000-0000-000000000000",
#             "SendersPhone": "380660000000",
#             "CityRecipient": "00000000-0000-0000-0000-000000000000",
#             "Recipient": "00000000-0000-0000-0000-000000000000",
#             "RecipientAddress": "00000000-0000-0000-0000-000000000000",
#             "ContactRecipient": "00000000-0000-0000-0000-000000000000",
#             "RecipientsPhone": "380660000000"
#         }
#     }

######################################
#  rate_user -> оценка пользователя  #
######################################

@login_required
def rate_user(request, username):
    if request.method == "POST":
        rating = int(request.POST.get("rating", 0))
        user = services.get_user_by_username(username)

        try:
            request.user.rate_(rating, user)
        except ValueError as e:
            error_message = str(e)
            messages.error(request, error_message)  # Добавляем сообщение об ошибке
        else:
            messages.success(request,
                             f"Вы успешно оценили пользователя {user.username}!")  # Добавляем сообщение об успехе
    prev_url = request.META.get("HTTP_REFERER", "home")
    return redirect(prev_url)


#############################################################################################
#     top_rated_users -> обработчик для пользователей, у которых рейтинг больше 4           #
#############################################################################################

def top_rated_users(request):
    users = services.get_users_with_high_ratings()
    return render(request, "products/new/top_rated_users.html", {"users": users})


def subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            # Настройте параметры SMTP-сервера
            smtp_host = EMAIL_HOST  # Замените на адрес вашего SMTP-сервера
            smtp_port = EMAIL_PORT  # Замените на порт вашего SMTP-сервера
            smtp_username = EMAIL_HOST_USER  # Замените на свое имя пользователя SMTP
            smtp_password = EMAIL_HOST_PASSWORD  # Замените на свой пароль SMTP

            # Создайте сообщение
            subject = 'Subscription Confirmation'
            message = f'Thank you for subscribing! Click the link to visit our website: http://127.0.0.1:8000/'
            from_email = EMAIL_HOST_USER  # Замените на вашу электронную почту
            to_email = email

            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = subject

            body = message
            msg.attach(MIMEText(body, 'plain'))

            # Отправьте сообщение через SMTP
            try:
                server = smtplib.SMTP(smtp_host, smtp_port)
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.sendmail(from_email, to_email, msg.as_string())
                server.quit()

                return redirect("home")

            except Exception as e:
                print(e)

    return render(request, 'products/new/footer.html')





