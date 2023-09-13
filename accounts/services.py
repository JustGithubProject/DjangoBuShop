from django.shortcuts import redirect
from django.contrib import messages


def handle_registration(request, form):
    if form.is_valid():
        if form.cleaned_data.get("captcha"):
            form.save()
            return redirect('login')
        else:
            messages.error(request, "Please complete the reCAPTCHA.")
    else:
        form.add_error(None, 'Invalid username or password.')
        messages.error(request, "Что-то пошло не так. Попробуйте еще раз")