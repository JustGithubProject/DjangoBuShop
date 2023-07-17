from django import forms

from .models import Product


class ProductForm(forms.ModelForm):
    """The Form to create a product"""
    class Meta:
        model = Product
        fields = ["title", "category", "description", "price", "image_1", "image_2", "image_3"]
