from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def vendeur_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("accounts:login")
        if not request.user.is_vendeur:
            messages.error(request, "Accès réservé aux comptes vendeur.")
            return redirect("accounts:dashboard")
        return view_func(request, *args, **kwargs)

    return _wrapped


def client_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("accounts:login")
        if not request.user.is_client:
            messages.error(request, "Accès réservé aux comptes client.")
            return redirect("accounts:dashboard")
        return view_func(request, *args, **kwargs)

    return _wrapped
