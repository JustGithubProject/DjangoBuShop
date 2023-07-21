from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import RegistrationForm, LoginForm


def registration_view(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, "registration.html", {'form': form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                form.add_error(None, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, "login.html", {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


def profile(request):
    if request.method == "POST":
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

        return redirect('profile')

    return render(request, 'profile.html', {'user': request.user})