from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from .models import User, VendorProfile


class ClientSignUpForm(UserCreationForm):
    """Formulaire d'inscription pour les clients."""

    email = forms.EmailField(required=True, label="Email")
    phone = forms.CharField(required=False, label="Téléphone")
    address = forms.CharField(required=False, label="Adresse")

    class Meta:
        model = User
        fields = ["username", "email", "phone", "address", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.CLIENT
        user.email = self.cleaned_data["email"]
        user.phone = self.cleaned_data.get("phone", "")
        user.address = self.cleaned_data.get("address", "")
        if commit:
            user.save()
        return user


class VendeurSignUpForm(UserCreationForm):
    """Formulaire d'inscription pour les vendeurs (crée aussi le profil boutique)."""

    email = forms.EmailField(required=True, label="Email")
    phone = forms.CharField(required=False, label="Téléphone")
    shop_name = forms.CharField(required=True, label="Nom de la boutique")
    shop_description = forms.CharField(
        required=False, widget=forms.Textarea, label="Description de la boutique"
    )

    class Meta:
        model = User
        fields = ["username", "email", "phone", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.VENDEUR
        user.email = self.cleaned_data["email"]
        user.phone = self.cleaned_data.get("phone", "")
        if commit:
            user.save()
            VendorProfile.objects.create(
                user=user,
                shop_name=self.cleaned_data["shop_name"],
                description=self.cleaned_data.get("shop_description", ""),
            )
        return user


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone", "address"]


class VendorProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = VendorProfile
        fields = ["shop_name", "description", "logo"]
