from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name="home"),
    path('search/', views.search_view, name='search'),
    path('product/<slug:slug>/', views.product_detail_view, name='product_detail'),
    path('create-chat/<slug:slug>/', views.create_chat_view, name="create_chat"),
    path("seller-messages/<slug:slug>/", views.seller_messages, name="seller_messages"),
    path('chat/<int:chat_id>/', views.chat_view, name="chat"),
    path('send-message/<int:chat_id>/', views.send_message_view, name='send_message'),
    path('user-buying-products/', views.user_buy, name="user_buy"),
    path('user-selling-products/', views.user_sell, name="user_sell"),
    path('create/post-product-add/', views.create_product, name='create_product'),
    path("create_order/<int:product_id>/", views.create_order, name="create_order"),
    path("view-orders-of-user-account/", views.orders_of_user, name="orders_of_user"),
    path('delete_chat/<int:chat_id>/', views.delete_chat, name='delete_chat'),
    path('delete_review/<int:review_id>/', views.delete_review, name="delete_review"),
    path('get-document-tracking/<str:tracking_number>/', views.get_document_tracking, name='get_document_tracking'),
    path("package_search/", views.package_search, name="package_search"),
    path("get-products-from-inventory/", views.get_products, name="get_products"),
    path('rate_user/<str:username>/', views.rate_user, name='rate_user'),
    path('top_rated_users', views.top_rated_users, name='top_rated_users'),
    path("subscribe/", views.subscribe, name="subscribe"),
    path("add_to_cart/<int:product_id>", views.add_to_cart, name="add_to_cart"),
    path("user-shopping-cart-contents/", views.get_cart, name="cart"),
    path("delete_cart<int:product_id>/", views.delete_cart, name="delete_cart"),
    path("create_order_cart/", views.create_order_cart, name="create_order_cart"),
    path("orders_of_user_from_cart/", views.orders_of_user_from_cart, name="orders_of_user_from_cart"),
    path("create_invoice/", views.create_invoice, name="create_invoice"),
    path("package_create/", views.package_create, name="package_create")
]