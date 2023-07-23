from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import password_reset

urlpatterns = [
    path('register/', views.registration_view, name="register"),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name="logout"),
    path('profile/', views.profile, name='profile'),
    path('reset_password/', password_reset,  name='password_reset'),
    path('reset_password/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]