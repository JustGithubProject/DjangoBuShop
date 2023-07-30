from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.contrib import messages

from .utils import transliterate
from .forms import ProductForm, OrderForm
from .models import Chat
from .models import Message
from .models import Order
from .models import Product
from .models import Category


################################################################
# home_view --> Главная страница с пагинацией                  #
################################################################

# @cache_page(300)
def home_view(request):
    categories = Category.objects.all()
    selected_category_id = request.GET.get('category')

    if selected_category_id:
        products = Product.objects.filter(category__slug=selected_category_id)
    else:
        products = Product.objects.order_by('-created_at')[:10]

    paginator = Paginator(products, 9)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, 'products/index.html',
                  {'categories': categories, 'products': page_obj, 'selected_category_id': selected_category_id})


################################################################
# search_view --> Поле поиска                                  #
################################################################


def search_view(request):
    query = request.GET.get("query")

    products = Product.objects.filter(title__icontains=query)
    context = {
        'query': query,
        'products': products,
    }
    return render(request, 'products/search_results.html', context)


###############################################################################################################
# product_detail_view --> Детально про продукт, где можно написать продавцу или продавцу посмотреть сообщения #
###############################################################################################################
# @cache_page(300)
def product_detail_view(request, slug):
    product = get_object_or_404(Product.objects.select_related('user'), slug=slug)
    return render(request, 'products/product_detail.html', {'product': product})


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


def seller_messages(request, slug):
    product = get_object_or_404(Product, slug=slug)

    chats = Chat.objects.filter(receiver=request.user, product=product)
    return render(request, "products/seller_messages.html", {"chats": chats, "product": product})


#######################################################
#  user_buy --> чаты, где пользователь что-то покупает#
#######################################################


def user_buy(request):
    chats = Chat.objects.filter(sender=request.user).select_related('receiver')
    temp = "buy"
    return render(request, "products/buy.html", {"chats": chats, "temp": temp})


#######################################################
#  user_sell --> чаты, где пользователь что-то продает#
#######################################################
def user_sell(request):
    chats = Chat.objects.filter(receiver=request.user).select_related('sender')
    temp = "sell"
    return render(request, "products/sell.html", {"chats": chats, "temp": temp})


@login_required
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


@login_required
def orders_of_user(request):
    orders = Order.objects.filter(customer_name=request.user)
    paginator = Paginator(orders, 1)  # Показывать по 10 заказов на странице (можешь изменить на свое усмотрение)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "products/orders.html", {"page_obj": page_obj})


############################################################
# zoomed_images -> Обработчик для увеличенных изображений  #
############################################################

def zoomed_images(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'products/zoomed_images.html', {'product': product})


def delete_chat(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)

    if chat.receiver == request.user or chat.sender == request.user:
        chat.delete()
        return redirect("user_sell")
    else:
        return HttpResponse("У вас нет прав на удаление этого чата.")

