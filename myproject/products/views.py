# products/views.py
from django.shortcuts import render, get_object_or_404
from .models import Product, Category
# Optional: If you need the search form
# from .forms import ProductSearchForm

def product_list(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'products/product_list.html', context)

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    context = {
        'product': product,
    }
    return render(request, 'products/product_detail.html', context)

def category_products(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category)
    categories = Category.objects.all()
    context = {
        'category': category,
        'products': products,
        'categories': categories,
    }
    return render(request, 'products/product_list.html', context)

def search_products(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(name__icontains=query) if query else Product.objects.none()
    categories = Category.objects.all()
    
    context = {
        'products': products,
        'categories': categories,
        'query': query
    }
    return render(request, 'products/product_list.html', context)