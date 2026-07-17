from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .decorators import client_required, vendeur_required
from .forms import (
    ClientSignUpForm,
    UserUpdateForm,
    VendeurSignUpForm,
    VendorProfileUpdateForm,
)
from .models import User


def choose_role(request):
    """Page d'accueil de l'inscription : choisir Client ou Vendeur."""
    return render(request, "accounts/choose_role.html")


def signup_client(request):
    if request.method == "POST":
        form = ClientSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Compte client créé avec succès !")
            return redirect("accounts:dashboard")
    else:
        form = ClientSignUpForm()
    return render(request, "accounts/signup.html", {"form": form, "role": "Client"})


def signup_vendeur(request):
    if request.method == "POST":
        form = VendeurSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Compte vendeur créé avec succès !")
            return redirect("accounts:dashboard")
    else:
        form = VendeurSignUpForm()
    return render(request, "accounts/signup.html", {"form": form, "role": "Vendeur"})


@login_required
def dashboard(request):
    """Redirige vers le bon tableau de bord selon le rôle."""
    if request.user.is_vendeur:
        return redirect("accounts:vendeur_dashboard")
    return redirect("accounts:client_dashboard")


@client_required
def client_dashboard(request):
    return render(request, "accounts/client_dashboard.html")


@vendeur_required
def vendeur_dashboard(request):
    return render(request, "accounts/vendeur_dashboard.html")


@login_required
def profile(request):
    user_form = UserUpdateForm(instance=request.user)
    vendor_form = None

    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=request.user)
        forms_valid = user_form.is_valid()

        if request.user.is_vendeur:
            vendor_form = VendorProfileUpdateForm(
                request.POST, request.FILES, instance=request.user.vendor_profile
            )
            forms_valid = forms_valid and vendor_form.is_valid()

        if forms_valid:
            user_form.save()
            if vendor_form:
                vendor_form.save()
            messages.success(request, "Profil mis à jour.")
            return redirect("accounts:profile")
    elif request.user.is_vendeur:
        vendor_form = VendorProfileUpdateForm(instance=request.user.vendor_profile)

    return render(
        request,
        "accounts/profile.html",
        {"user_form": user_form, "vendor_form": vendor_form},
    )
