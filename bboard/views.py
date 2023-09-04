import requests
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.contrib import messages
from django.views.decorators.cache import cache_page

from accounts.models import User
from project import settings
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


################################################################
# home_view --> Главная страница                               #
################################################################


def home_view(request):
    products = Product.objects.order_by('-created_at').select_related('user')[:5]
    reviews = Review.objects.order_by("date_posted").select_related('reviewer_name')[:10]

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.reviewer_name = request.user
            review.save()
            return redirect("home")
        else:
            print(form.errors)
    else:
        form = ReviewForm()
    quantity_users = User.objects.count()
    return render(request, "products/new/index.html",
                  {"products": products, "form": form, "reviews": reviews, "quantity_users": quantity_users})


#######################################################################
#    delete_review -> удалить  комментарий                            #
#######################################################################


def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    if request.user.is_superuser:
        review.delete()
        return redirect("home")
    else:
        return HttpResponse("У вас нет прав на удаление этого комментария")


################################################################
# search_view --> Поле поиска                                  #
################################################################


def search_view(request):
    query = request.GET.get("query")

    if not query:
        products = None
    else:
        products = Product.objects.filter(title__icontains=query)
    context = {
        'query': query,
        'products': products,
    }
    return render(request, 'products/search_results.html', context)


#############################################
#    get_products   -> все товары           #
#############################################

def get_products(request):
    categories = Category.objects.all()
    selected_category_id = request.GET.get('category')

    if selected_category_id:
        products = Product.objects.filter(category__slug=selected_category_id)
    else:
        products = Product.objects.order_by('-created_at')[:10]

    paginator = Paginator(products, 9)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, 'products/new/product.html',
                  {'categories': categories, 'products': page_obj, 'selected_category_id': selected_category_id})


###############################################################################################################
# product_detail_view --> Детально про товар, где можно написать продавцу или продавцу посмотреть сообщения #
###############################################################################################################

def product_detail_view(request, slug):
    product = get_object_or_404(Product.objects.select_related('user'), slug=slug)
    return render(request, 'products/product_detail.html', {'product': product, 'messages': messages})


##############################################################################################################
# create_chat_view --> обработчик для перехода в чат(если он существует) или создания чата и перехода к нему #
##############################################################################################################

@login_required
def create_chat_view(request, slug):
    product = get_object_or_404(Product, slug=slug)

    if not request.user.is_authenticated:
        return redirect("login")

    # Проверяем существование чата между отправителем и получателем
    chat_exists = Chat.objects.filter(sender=request.user, receiver=product.user, product=product).first()

    if chat_exists:
        # Если чат уже существует, перенаправляем пользователя на страницу чата
        return redirect("chat", chat_id=chat_exists.id)

    # Если чат не существует, создаем его
    chat = Chat.objects.create(sender=request.user, receiver=product.user, product=product)
    return redirect("chat", chat_id=chat.id)


################################################
# chat_view --> чат между двумя пользователями #
################################################
@login_required
def chat_view(request, chat_id):
    chat = get_object_or_404(Chat.objects.select_related('receiver'), id=chat_id)
    if request.user != chat.sender and request.user != chat.receiver:
        return HttpResponse("У вас нет доступа к этому чату.")
    messages = Message.objects.filter(chat=chat).order_by('created_at').select_related('sender')

    return render(request, "products/chat.html", {"chat": chat, "messages": messages})


###############################################################################################
# send_message_view --> отправка сообщений, и редирект для того, чтобы страница обновилась    #
###############################################################################################

@login_required
def send_message_view(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)

    # Проверяем, авторизован ли пользователь
    if not request.user.is_authenticated:
        return redirect('login')  # Перенаправляем на страницу входа, если пользователь не авторизован

    # Проверяем, является ли текущий пользователь участником чата
    if request.user != chat.sender and request.user != chat.receiver:
        return HttpResponseForbidden("У вас нет доступа к этому чату")

    if request.method == 'POST':
        message_content = request.POST.get('message')

        # Создаем новое сообщение
        message = Message(chat=chat, sender=request.user, content=message_content)
        message.save()

        messages.success(request, 'Сообщение успешно отправлено')

    return redirect('chat', chat_id=chat_id)


####################################################################################
#    seller_messages --> продавец может посмотреть тех, кто оправлял ему сообщения #
####################################################################################

@login_required
def seller_messages(request, slug):
    product = get_object_or_404(Product, slug=slug)

    chats = Chat.objects.filter(receiver=request.user, product=product)
    return render(request, "products/seller_messages.html", {"chats": chats, "product": product})


#######################################################
#  user_buy --> чаты, где пользователь что-то покупает#
#######################################################

@login_required
def user_buy(request):
    chats = Chat.objects.filter(sender=request.user).select_related('receiver', 'product')

    temp = "buy"
    return render(request, "products/buy.html", {"chats": chats, "temp": temp})


#######################################################
#  user_sell --> чаты, где пользователь что-то продает#
#######################################################
@login_required
def user_sell(request):
    chats = Chat.objects.filter(receiver=request.user).select_related('sender')
    temp = "sell"
    return render(request, "products/sell.html", {"chats": chats, "temp": temp})


################################################################################################
#    create_product ->  view для создания Товара, любой пользователь может добавить свой товар #
################################################################################################


@login_required
@cache_page(300)
def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user

            # Generate slug from title and transliterate if necessary
            title = form.cleaned_data['title']
            print(title)
            slug = transliterate(title)
            print(slug)
            product.slug = slug

            product.save()
            return redirect("home")
        else:
            print(form.errors)
    else:
        form = ProductForm()
    return render(request, 'products/create_product.html', {'form': form})


########################################################
#    create_order -> Делает заказ и сохраняет его в бд #
########################################################


@login_required
def create_order(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    if request.method == "POST" and request.user != product.user:
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.customer_name = request.user
            order.product = product
            order.save()
            return redirect("home")
        else:
            print(form.errors)
    else:
        form = OrderForm()

    return render(request, "products/create_order.html", {"form": form})


###########################################################
# orders_of_users -> Все заказы определенного пользователя#
###########################################################

@login_required
def orders_of_user(request):
    orders = Order.objects.select_related('product__user').filter(customer_name=request.user)

    paginator = Paginator(orders, 1)  # Показывать по 10 заказов на странице (можешь изменить на свое усмотрение)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "products/orders.html", {"page_obj": page_obj})


#########################################################################################
#    delete_chat -> view для удаления чата, каждый пользователь может удалить свои чаты #
#########################################################################################


def delete_chat(request, chat_id):
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
    """Информация о посылке по накладной"""
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

def rate_user(request, username):
    if request.method == "POST":
        rating = int(request.POST.get("rating", 0))
        user = User.objects.get(username=username)

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
