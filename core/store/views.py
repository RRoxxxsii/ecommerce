from django.shortcuts import render, get_object_or_404
from .models import Product, Category


def pageNotFound(request, exception):
    return render(request, '404.html')


def product_all(request):
    products = Product.objects.prefetch_related("product_image").filter(is_active=True)
    return render(request, 'store/home.html', {'products': products})


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, 'store/products/detail.html', {'product': product})


def category_list(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(category__in=Category.objects.get(name=category_slug).get_descendants(include_self=True))
    return render(request, 'store/products/category.html', {'category': category, 'products': products})



