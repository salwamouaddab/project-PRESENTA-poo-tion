from django.urls import path

from . import views

app_name = "cart"

urlpatterns = [
    path("", views.view_cart, name="view_cart"),
    path("ajouter/<slug:slug>/", views.add_to_cart, name="add_to_cart"),
    path("item/<int:item_id>/modifier/", views.update_cart_item, name="update_cart_item"),
    path("item/<int:item_id>/retirer/", views.remove_from_cart, name="remove_from_cart"),
]
