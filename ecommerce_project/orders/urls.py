from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("checkout/", views.checkout, name="checkout"),
    path("", views.order_list, name="order_list"),
    path("<int:order_id>/", views.order_detail, name="order_detail"),
    path("vendeur/", views.vendeur_order_list, name="vendeur_order_list"),
    path("vendeur/<int:order_id>/statut/", views.update_order_status, name="update_order_status"),
]
