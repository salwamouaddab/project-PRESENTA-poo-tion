from django.urls import path

from . import views

app_name = "products"

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("mine/", views.my_products, name="my_products"),
    path("mine/ajouter/", views.product_create, name="product_create"),
    path("mine/<slug:slug>/modifier/", views.product_update, name="product_update"),
    path("mine/<slug:slug>/supprimer/", views.product_delete, name="product_delete"),
    path("<slug:slug>/", views.product_detail, name="product_detail"),
]
