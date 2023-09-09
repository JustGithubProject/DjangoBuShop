from django.core.paginator import Paginator
from django.shortcuts import redirect

from .models import Category
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