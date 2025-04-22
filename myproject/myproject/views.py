# Add these imports to the top of your views.py files as needed

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *  # Replace with specific models
from .forms import *  # Replace with specific forms
from django.shortcuts import render
from products.models import Product

def home_view(request):
    featured_products = Product.objects.all().order_by('-created_at')[:4]
    context = {
        'featured_products': featured_products
    }
    return render(request, 'home.html', context)