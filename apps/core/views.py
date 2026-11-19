
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
from .forms import ProductForm


def home(request):
    products = Product.objects.all()

    return render(
        request,
        "core/home.html",
        {"products": products}
    )


def product_list(request):
    products = Product.objects.all()

    return render(
        request,
        "core/product_list.html",
        {"products": products}
    )



def product_create(request):

    if request.method == "POST":
        form = ProductForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("product_list")

    else:
        form = ProductForm()

    return render(
        request,
        "core/product_form.html",
        {"form": form}
    )



def product_edit(request, pk):

    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)

        if form.is_valid():
            form.save()
            return redirect("product_list")

    else:
        form = ProductForm(instance=product)

    return render(
        request,
        "core/product_form.html",
        {"form": form}
    )


def product_delete(request, pk):

    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        product.delete()
        return redirect("product_list")

    return render(
        request,
        "core/product_confirm_delete.html",
        {"product": product}
    )














