from django import forms

from .models import Product, Order


class ProductForm(forms.ModelForm):
    """The Form to create a product"""
    class Meta:
        model = Product
        fields = ["title", "category", "description", "price", "image_1", "image_2", "image_3"]


class OrderForm(forms.ModelForm):
    """The Form to create a order"""
    class Meta:
        model = Order
        fields = ["quantity", "customer_email", "shipping_address"]