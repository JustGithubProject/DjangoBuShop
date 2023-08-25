from django import forms
from django.core.exceptions import ValidationError

from .models import Product, Order, Review


class ProductForm(forms.ModelForm):
    """The Form to create a product"""
    class Meta:
        model = Product
        fields = ["title", "category", "description", "price", "image_1", "image_2", "image_3"]


class OrderForm(forms.ModelForm):
    """The Form to create a order"""
    class Meta:
        model = Order
        fields = ["name", "surname", "city", "department", "phone_number", "email"]


class ReviewForm(forms.ModelForm):
    """The form for review"""

    class Meta:
        model = Review
        fields = ["content"]

    def clean_content(self):
        content = self.cleaned_data.get("content")

        if len(content) < 10:
            raise ValidationError("Должно быть больше 10 символов")
        if content.isdigit() or content[0].isdigit():
            raise ValidationError("Содержимое не может состоять только из цифр или начинаться с цифры.")

        return content