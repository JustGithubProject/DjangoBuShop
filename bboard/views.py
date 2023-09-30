from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.views.decorators.cache import cache_page

from .forms import OrderCartForm
from .forms import ReviewForm
from .models import Cart
from .models import CartItem
from .models import Review
from .utils import decode_status
from .forms import ProductForm
from .forms import OrderForm
from .models import Chat
from .models import Product
from . import services


def home_view(request):
    """home_view --> Главная страница   """
    products = services.get_recent_products_with_users()
    reviews = services.get_recent_reviews_with_reviewers()

    if services.process_review_form(request):
        return redirect("home")

    form = ReviewForm()

    quantity_users = services.get_user_count()
    unread_messages_count_per_user = services.get_unread_message_count(request.user)
    return render(request, "products/new/index.html",
                  {"products": products, "form": form, "reviews": reviews, "quantity_users": quantity_users,
                   "unread_messages_count_per_user": unread_messages_count_per_user})


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


@cache_page(60)
def get_products(request):
    categories = services.get_all_categories()
    selected_category_id = request.GET.get('category')
    products = services.get_products_by_category(selected_category_id)
    page_number = request.GET.get("page")
    page_obj = services.paginate_products(products, page_number)

    unread_messages_count_per_user = services.get_unread_message_count(request.user)

    return render(request, 'products/new/product.html',
                  {'categories': categories, 'products': page_obj, 'selected_category_id': selected_category_id,
                   "unread_messages_count_per_user": unread_messages_count_per_user})


def product_detail_view(request, slug):
    """
    product_detail_view --> Детально про товар, где можно написать продавцу или продавцу посмотреть сообщения
    """
    product = get_object_or_404(Product.objects.select_related('user'), slug=slug)
    unread_messages_count_per_user = services.get_unread_message_count(request.user)
    return render(request, 'products/product_detail.html', {'product': product, 'messages': messages,
                                                            "unread_messages_count_per_user": unread_messages_count_per_user})


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

    for message in messages:
        if not message.read and message.sender != request.user:
            message.read = True
            message.save()

    unread_messages_count_per_user = services.get_unread_message_count(request.user)

    return render(request, "products/chat.html", {"chat": chat, "messages": messages,
                                                  "unread_messages_count_per_user": unread_messages_count_per_user})


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
    unread_messages_count_per_user = services.get_unread_message_count(request.user)
    return render(request, "products/seller_messages.html", {"chats": chats, "product": product,
                                                             "unread_messages_count_per_user": unread_messages_count_per_user})


@login_required
def user_buy(request):
    """
    user_buy --> чаты, где пользователь что-то покупает
    """
    chats = services.get_user_chats(request.user, chat_type="buy")
    unread_messages_count_per_user = services.get_unread_message_count(request.user)
    return render(request, "products/buy.html",
                  {"chats": chats, "temp": "buy", "unread_messages_count_per_user": unread_messages_count_per_user})


@login_required
def user_sell(request):
    """
    user_sell --> чаты, где пользователь что-то продает
    """
    chats = services.get_user_chats(request.user, chat_type="sell")
    unread_messages_count_per_user = services.get_unread_message_count(request.user)
    return render(request, "products/sell.html",
                  {"chats": chats, "temp": "sell", "unread_messages_count_per_user": unread_messages_count_per_user})


@login_required
@cache_page(20)
def create_product(request):
    """
    Создание нового товара.

    Это представление позволяет любому пользователю добавить свой товар на сайт. Пользователь может заполнить форму
    с данными о товаре и загрузить изображение товара. После успешного создания товара, пользователь будет перенаправлен
    на домашнюю страницу.

    Кеширование: Это представление кешируется на 20 секунд, что помогает снизить нагрузку на сервер и ускорить
    отображение страницы при повторных запросах в течение этого времени.

    :param request: Объект запроса Django.
    :return: Перенаправление на домашнюю страницу после успешного создания товара или отображение формы создания товара.
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

    unread_messages_count_per_user = services.get_unread_message_count(request.user)
    return render(request, 'products/create_product.html',
                  {'form': form, "unread_messages_count_per_user": unread_messages_count_per_user})


@login_required
def create_order(request, product_id):
    """
    Создание заказа для продукта.

    Это представление позволяет пользователю создать заказ для определенного продукта и сохранить его в базе данных.
    Для создания заказа необходимо заполнить форму с данными о заказе. Пользователь может создать заказ только
    для продукта, который не принадлежит ему.

    :param request: Объект запроса Django.
    :param product_id: Идентификатор продукта, для которого создается заказ.
    :return: Перенаправление на домашнюю страницу после успешного создания заказа или отображение формы заказа.
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

    unread_messages_count_per_user = services.get_unread_message_count(request.user)

    return render(request, "products/create_order.html",
                  {"form": form, "unread_messages_count_per_user": unread_messages_count_per_user})


@login_required
def orders_of_user(request):
    """
    orders_of_user -> Просмотр всех заказов определенного пользователя.

    Это представление отображает список всех заказов, сделанных определенным пользователем.
    Пользователь должен быть авторизован для доступа к этой странице.

    :param request: Объект запроса Django.
    :return: Ответ с отображением списка заказов пользователя.
    """
    orders = services.get_user_orders(request.user)
    page_obj = services.paginate_orders(request, orders)

    unread_messages_count_per_user = services.get_unread_message_count(request.user)
    return render(request, "products/orders.html",
                  {"page_obj": page_obj, "unread_messages_count_per_user": unread_messages_count_per_user})


def delete_chat(request, chat_id):
    """
    Удаление чата.

    Это представление позволяет пользователю удалить чат. Каждый пользователь может удалять только свои чаты.
    Если пользователь является отправителем или получателем чата, чат будет удален. В противном случае пользователь
    не имеет прав на удаление чата.

    :param request: Объект запроса Django.
    :param chat_id: Идентификатор чата, который нужно удалить.
    :return: Перенаправление на страницу с чатами пользователя после успешного удаления, или сообщение об ошибке.
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
    Получение информации о трекинге документа.

    Это представление позволяет пользователю получить информацию о трекинге документа по его
    уникальному номеру. Информация включает в себя вес документа, стоимость доставки, статус,
    номер с квадры, город отправителя и город получателя.

    :param request: Объект запроса Django.
    :param tracking_number: Уникальный номер трекинга документа.
    :return: Ответ с информацией о трекинге или JSON-ответ с ошибкой, если данные не найдены.
    """
    tracking_data = services.fetch_tracking_info(tracking_number)

    if tracking_data:
        weight = tracking_data.get("DocumentWeight")
        cost_of_delivery = tracking_data.get("DocumentCost")
        status_code = tracking_data.get("StatusCode")
        status_code_decoding = decode_status.get(str(status_code), "Unknown")
        number_squad = tracking_data.get("WarehouseRecipientNumber")
        city_sender = tracking_data.get("CitySender")
        decoded_city_sender = city_sender.encode().decode()
        city_recipient = tracking_data.get("CityRecipient")
        decoded_city_recipient = city_recipient.encode().decode()

        context = {
            "weight": weight,
            "cost_of_delivery": cost_of_delivery,
            "status_code_decoding": status_code_decoding,
            "number_squad": number_squad,
            "decoded_city_sender": decoded_city_sender,
            "decoded_city_recipient": decoded_city_recipient
        }

        return render(request, "products/get_document_tracking.html", context=context)
    else:
        return JsonResponse({"error": "Tracking data not found"}, status=404)


##################################################################################################
#  package_search -> обработчик для формы, которая ищет информацию по декларации новой почты     #
##################################################################################################


def package_search(request):
    """
    Поиск информации о трекинге документа по номеру декларации.

    Это представление обрабатывает GET-запрос, в котором пользователь указывает номер декларации.
    Если номер декларации указан, представление перенаправляет пользователя на страницу с информацией
    о трекинге документа, используя представление `get_document_tracking`. Если номер декларации не
    указан, представление отображает страницу поиска декларации.

    :param request: Объект запроса Django.
    :return: Перенаправление на страницу с информацией о трекинге или страницу поиска декларации.
    """
    declaration = request.GET.get("package_number")
    if declaration:
        return redirect('get_document_tracking', declaration)

    unread_messages_count_per_user = services.get_unread_message_count(request.user)
    return render(request, "products/package_search.html",
                  {"declaration": declaration, "unread_messages_count_per_user": unread_messages_count_per_user})


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
    """
    Оценка пользователя.

    Это представление позволяет пользователю оценить другого пользователя на сайте.
    Пользователь может указать рейтинг в форме POST-запроса. Если оценка прошла
    успешно, добавляется сообщение об успехе, в противном случае добавляется сообщение об ошибке.

    :param request: Объект запроса Django.
    :param username: Имя пользователя, которого пользователь хочет оценить.
    :return: Перенаправление на предыдущую страницу с сообщением об успехе или ошибке.
    """
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
    """
    Просмотр пользователей с высоким рейтингом.

    Это представление отображает список пользователей, у которых есть высокие рейтинги
    на вашем сайте или в вашем приложении.

    :param request: Объект запроса Django.
    :return: Ответ с отображением списка пользователей с высокими рейтингами.
    """
    users = services.get_users_with_high_ratings()
    return render(request, "products/new/top_rated_users.html", {"users": users})


def subscribe(request):
    """
    Подписка пользователя на рассылку.

    Это представление обрабатывает POST-запрос, в котором пользователь вводит свой
    адрес электронной почты для подписки на рассылку. После успешной подписки
    отправляется подтверждение на указанный адрес электронной почты.

    :param request: Объект запроса Django.
    :return: Перенаправление на домашнюю страницу после успешной подписки.
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            if services.send_subscription_confirmation(email):
                return redirect("home")

    return render(request, 'products/new/footer.html')


@login_required
def add_to_cart(request, product_id):
    """
    Добавление товара в корзину пользователя.

    Это представление обрабатывает запрос на добавление выбранного товара в корзину пользователя.

    :param request: Объект запроса Django.
    :param product_id: Идентификатор товара, который нужно добавить в корзину.
    :return: Перенаправление на страницу корзины после успешного добавления товара.
    """
    product = services.get_product_by_id(product_id)
    user_cart, created = services.get_or_create_cart_by_user(request.user)

    cart_item, created = services.get_or_create_cart_item_by_cart_and_product(user_cart, product)

    return redirect("cart")


@login_required
def get_cart(request):
    """
    Просмотр корзины пользователя.

    Это представление отображает содержимое корзины пользователя и вычисляет общую стоимость
    продуктов в корзине.

    :param request: Объект запроса Django.
    :return: Ответ с отображением содержимого корзины и общей стоимостью.
    """
    cart = Cart.objects.get(user=request.user)
    items = cart.products.all()
    quantity_dict = {item.id: CartItem.objects.get(cart=cart, product_id=item.id) for item in items}
    total_price = 0
    for item in items:
        total_price += quantity_dict[item.id].product.price

    unread_messages_count_per_user = services.get_unread_message_count(request.user)
    return render(request, "products/new/cart.html", {"items": items, "quantity_dict": quantity_dict,
                                                      "total_price": total_price,
                                                      "unread_messages_count_per_user": unread_messages_count_per_user})


def delete_cart(request, product_id):
    """
    Удаление продукта из корзины пользователя.

    Это представление удаляет выбранный продукт из корзины пользователя.

    :param request: Объект запроса Django.
    :param product_id: Идентификатор продукта, который нужно удалить.
    :return: Перенаправление на текущую страницу.
    """
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
    cart_item.delete()
    return redirect(request.META.get("HTTP_REFERER", "home"))


def create_order_cart(request):
    """
      Создание заказа из корзины пользователя.

      Это представление обрабатывает форму, создающую заказ на основе содержимого корзины
      пользователя.

      :param request: Объект запроса Django.
      :return: Перенаправление на домашнюю страницу после создания заказа.
    """
    if request.method == "POST":
        form = OrderCartForm(request.POST)
        if form.is_valid():
            if services.create_order_from_cart(request.user, form):
                return redirect("home")
        else:
            print(form.errors)
    else:
        form = OrderCartForm()
    unread_messages_count_per_user = services.get_unread_message_count(request.user)
    return render(request, "products/new/create_order_cart.html",
                  {"form": form, "unread_messages_count_per_user": unread_messages_count_per_user})


def orders_of_user_from_cart(request):
    """
    Просмотр заказов, созданных из корзины пользователя.

    Это представление отображает список заказов, которые были созданы из корзины
    пользователя.

    :param request: Объект запроса Django.
    :return: Ответ с отображением списка заказов.
    """
    orders = services.get_orders_from_cart(request.user)
    page_obj = services.paginate_orders(request, orders)

    unread_messages_count_per_user = services.get_unread_message_count(request.user)
    return render(request, "products/new/orders_of_cart.html",
                  {"page_obj": page_obj, "unread_messages_count_per_user": unread_messages_count_per_user})
