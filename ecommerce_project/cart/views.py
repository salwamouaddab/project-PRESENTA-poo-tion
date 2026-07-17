from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import client_required
from products.models import Product

from .models import Cart, CartItem


@client_required
def view_cart(request):
    cart, _ = Cart.objects.get_or_create(client=request.user)
    return render(request, "cart/cart_detail.html", {"cart": cart})


@client_required
def add_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    cart, _ = Cart.objects.get_or_create(client=request.user)

    quantity = int(request.POST.get("quantity", 1)) if request.method == "POST" else 1

    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        item.quantity += quantity
    else:
        item.quantity = quantity
    item.quantity = min(item.quantity, product.stock) if product.stock else item.quantity
    item.save()

    messages.success(request, f"« {product.name} » ajouté au panier.")
    return redirect("cart:view_cart")


@client_required
def update_cart_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__client=request.user)
    if request.method == "POST":
        quantity = int(request.POST.get("quantity", 1))
        if quantity <= 0:
            item.delete()
        else:
            item.quantity = quantity
            item.save()
    return redirect("cart:view_cart")


@client_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__client=request.user)
    item.delete()
    messages.info(request, "Produit retiré du panier.")
    return redirect("cart:view_cart")
