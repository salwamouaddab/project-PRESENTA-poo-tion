from django import forms
from django.utils.text import slugify

from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "category", "description", "price", "stock", "image", "is_active"]

    def save(self, commit=True):
        product = super().save(commit=False)
        if not product.slug:
            product.slug = slugify(product.name)
        if commit:
            product.save()
        return product
