from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.choose_role, name="choose_role"),
    path("signup/client/", views.signup_client, name="signup_client"),
    path("signup/vendeur/", views.signup_vendeur, name="signup_vendeur"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="accounts/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(next_page="accounts:login"), name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/client/", views.client_dashboard, name="client_dashboard"),
    path("dashboard/vendeur/", views.vendeur_dashboard, name="vendeur_dashboard"),
    path("profile/", views.profile, name="profile"),
]
