from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from .forms import CustomPasswordResetEmailForm
from .forms import RegistrationForm
from .forms import LoginForm
from .forms import CustomPasswordResetForm
from .models import User

from . import services


def registration_view(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        services.handle_registration(request, form)
    else:
        form = RegistrationForm()
    return render(request, "users/registration.html", {'form': form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data["password"]

            if services.handle_login(request, username, password):
                return redirect('home')
            else:
                form.add_error(None, 'Invalid username or password.')
                messages.error(request, "Введен неверный пароль!\n\rПроверьте раскладку клавиатуры и Caps Lock")

    else:
        form = LoginForm()
    return render(request, "users/login.html", {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


def profile(request):
    if request.method == "POST":
        services.get_and_update_fields(request)
        return redirect('profile')

    return render(request, 'users/profile.html', {'user': request.user})


def password_reset(request):
    if request.method == "POST":
        form = CustomPasswordResetEmailForm(request.POST)
        if form.is_valid():
            form.save(
                request=request,
                subject_template_name="registration/password_reset_subject.txt",
                email_template_name='registration/password_reset_email.html',
            )
            return redirect('password_reset_done')  # Вернуть редирект, если форма допустима
    else:
        form = CustomPasswordResetEmailForm()
    return render(request, "users/password_reset_form.html", {'form': form})  # Вернуть render вне блока else


def custom_password_reset_confirm(request, uidb64, token):
    # Декодируем uidb64 для получения пользователя
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = services.get_user_by_uid(uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = CustomPasswordResetForm(request.user, request.POST)  # Передаем user в форму
            if form.is_valid():
                new_password = form.cleaned_data['new_password1']
                user.set_password(new_password)
                user.save()
                return redirect('login')
        else:
            form = CustomPasswordResetForm(user)  # Передаем user в форму
    else:
        return redirect('password_reset_done')

    return render(request, 'users/password_reset_confirm.html', {'form': form})


def password_reset_done(request):
    return render(request, "users/password_reset_done.html")
