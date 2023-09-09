from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect

from .models import Category
from .models import Chat
from .models import Message
from .models import Product, Review
from accounts.models import User
from .forms import ReviewForm


####################################################################
#               БИЗНЕС ЛОГИКА ДЛЯ HOME_VIEW                        #
####################################################################

def get_recent_products_with_users():
    return Product.objects.order_by('-created_at').select_related('user')[:5]


def get_recent_reviews_with_reviewers():
    return Review.objects.order_by("date_posted").select_related('reviewer_name')[:10]


def process_review_form(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.reviewer_name = request.user
            review.save()
            return True  # Успешно обработано
    return False


def get_user_count():
    return User.objects.count()


####################################################################
#               БИЗНЕС ЛОГИКА  search_view                         #
####################################################################


def search_products(query):
    if not query:
        return None
    return Product.objects.filter(title__icontains=query)


#####################################################################
#               БИЗНЕС ЛОГИКА  get_products                         #
#####################################################################

def get_all_categories():
    return Category.objects.all()


def get_products_by_category(selected_category_id):
    if selected_category_id:
        return Product.objects.filter(category__slug=selected_category_id)
    return Product.objects.order_by('-created_at')[:10]


def paginate_products(products, page_number, per_page=9):
    paginator = Paginator(products, per_page)
    return paginator.get_page(page_number)


#####################################################################
#               БИЗНЕС ЛОГИКА  create_chat_view                     #
#####################################################################

def create_or_get_chat(sender, product):
    """
    Функция для создания нового чата или получения существующего чата между отправителем и получателем.
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
    """Retrieve chat and messages for the given user and chat_id."""
    chat = get_object_or_404(Chat.objects.select_related('receiver'), id=chat_id)

    if user != chat.sender and user != chat.receiver:
        return None, None

    messages = Message.objects.filter(chat=chat).order_by('created_at').select_related('sender')
    return chat, messages


#####################################################################
#               БИЗНЕС ЛОГИКА  send_message_view                    #
#####################################################################

def create_and_save_message(chat, sender, content):
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
    """Возвращает чаты, где пользователь продавец и связаны с конкретным продуктом."""
    return Chat.objects.filter(receiver=user, product=product).select_related('sender', 'product')

#####################################################################
#               БИЗНЕС ЛОГИКА  user_buy  и user_sell                #
#####################################################################


def get_user_chats(user, chat_type):
    """Возвращает чаты в зависимости от типа (покупка или продажа)."""
    if chat_type == "buy":
        return Chat.objects.filter(sender=user).select_related('receiver', 'product')
    elif chat_type == "sell":
        return Chat.objects.filter(receiver=user).select_related('sender')
    else:
        # Обработка некорректного типа чата (по умолчанию показываем покупки)
        return Chat.objects.filter(sender=user).select_related('receiver', 'product')

