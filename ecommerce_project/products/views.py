from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import vendeur_required

from .forms import ProductForm
from .models import Category, Product


def product_list(request):
    """Page d'accueil publique : catalogue de tous les produits actifs."""
    products = Product.objects.filter(is_active=True, stock__gt=0)

    category_slug = request.GET.get("category")
    if category_slug:
        products = products.filter(category__slug=category_slug)

    query = request.GET.get("q")
    if query:
        products = products.filter(name__icontains=query)

    categories = Category.objects.all()
    return render(
        request,
        "products/product_list.html",
        {"products": products, "categories": categories},
    )


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, "products/product_detail.html", {"product": product})


@vendeur_required
def my_products(request):
    products = Product.objects.filter(vendeur=request.user)
    return render(request, "products/my_products.html", {"products": products})


@vendeur_required
def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.vendeur = request.user
            product.save()
            messages.success(request, "Produit ajouté avec succès.")
            return redirect("products:my_products")
    else:
        form = ProductForm()
    return render(request, "products/product_form.html", {"form": form, "action": "Ajouter"})


@vendeur_required
def product_update(request, slug):
    product = get_object_or_404(Product, slug=slug, vendeur=request.user)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Produit mis à jour.")
            return redirect("products:my_products")
    else:
        form = ProductForm(instance=product)
    return render(request, "products/product_form.html", {"form": form, "action": "Modifier"})


@vendeur_required
def product_delete(request, slug):
    product = get_object_or_404(Product, slug=slug, vendeur=request.user)
    if request.method == "POST":
        product.delete()
        messages.success(request, "Produit supprimé.")
        return redirect("products:my_products")
    return render(request, "products/product_confirm_delete.html", {"product": product})
