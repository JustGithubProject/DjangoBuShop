from django.contrib.auth import authenticate
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import login
from .models import User


def handle_registration(request, form):
    """Проверка валидности формы регистрации"""
    if form.is_valid():
        if form.cleaned_data.get("captcha"):
            form.save()
            return redirect('login')
        else:
            messages.error(request, "Please complete the reCAPTCHA.")
    else:
        form.add_error(None, 'Invalid username or password.')
        messages.error(request, "Что-то пошло не так. Попробуйте еще раз")


def handle_login(request, username, password):
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return True
    else:
        return False


def get_and_update_fields(request):
    # Получаем значения из формы
    username = request.POST.get('username')
    email = request.POST.get('email')
    first_name = request.POST.get('first_name')
    last_name = request.POST.get("last_name")
    phone_number = request.POST.get("phone_number")

    # Обновляем соответствующие поля профиля пользователя
    user = request.user
    user.username = username
    user.first_name = first_name
    user.email = email
    user.last_name = last_name
    user.phone_number = phone_number
    user.save()


def get_user_by_uid(uid):
    return User.objects.get(pk=uid)