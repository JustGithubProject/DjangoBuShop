from django.contrib.auth import authenticate
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import login


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