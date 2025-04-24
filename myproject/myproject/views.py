from django.shortcuts import render
from products.models import Product

def home_view(request):
    featured_products = Product.objects.all().order_by('-created_at')[:4]  
    context = {
        'featured_products': featured_products
    }
    return render(request, 'home.html', context)