from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import client_required, vendeur_required
from cart.models import Cart

from .models import Order, OrderItem


@client_required
def checkout(request):
    cart, _ = Cart.objects.get_or_create(client=request.user)
    if not cart.items.exists():
        messages.warning(request, "Votre panier est vide.")
        return redirect("cart:view_cart")

    if request.method == "POST":
        address = request.POST.get("shipping_address") or request.user.address
        if not address:
            messages.error(request, "Merci de renseigner une adresse de livraison.")
            return redirect("orders:checkout")

        with transaction.atomic():
            order = Order.objects.create(client=request.user, shipping_address=address)
            for item in cart.items.select_related("product"):
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    vendeur=item.product.vendeur,
                    quantity=item.quantity,
                    unit_price=item.product.price,
                )
                # Décrémente le stock
                item.product.stock = max(item.product.stock - item.quantity, 0)
                item.product.save()
            cart.items.all().delete()

        messages.success(request, f"Commande #{order.id} passée avec succès !")
        return redirect("orders:order_detail", order_id=order.id)

    return render(request, "orders/checkout.html", {"cart": cart})


@client_required
def order_list(request):
    orders = Order.objects.filter(client=request.user)
    return render(request, "orders/order_list.html", {"orders": orders})


@client_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, client=request.user)
    return render(request, "orders/order_detail.html", {"order": order})


@vendeur_required
def vendeur_order_list(request):
    """Commandes contenant au moins un produit du vendeur connecté."""
    items = OrderItem.objects.filter(vendeur=request.user).select_related("order", "product")
    orders = {}
    for item in items:
        orders.setdefault(item.order, []).append(item)
    return render(request, "orders/vendeur_order_list.html", {"orders": orders})


@vendeur_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id, items__vendeur=request.user)
    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in Order.Status.values:
            order.status = new_status
            order.save()
            messages.success(request, f"Statut de la commande #{order.id} mis à jour.")
    return redirect("orders:vendeur_order_list")
