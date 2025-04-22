# Add these imports to the top of your views.py files as needed

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cart  # Replace with specific models
from .forms import Product  # Replace with specific forms
@login_required
def cart_detail(request):
    # This function is already correctly named
    cart_items = Cart.objects.filter(user=request.user)
    cart_total = sum(item.get_total_price() for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'cart_total': cart_total,
    }
    return render(request, 'cart/cart_detail.html', context)

@login_required
def cart_add(request, product_id):  # Renamed from add_to_cart
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    
    # Check if the product is already in the cart
    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': quantity}
    )
    
    # If the product was already in the cart, increase the quantity
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    
    messages.success(request, f"{product.name} added to your cart.")
    return redirect('cart:cart_detail')

@login_required
def cart_remove(request, item_id):  # Renamed from remove_from_cart
    cart_item = get_object_or_404(Cart, id=item_id, user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    
    messages.success(request, f"{product_name} removed from your cart.")
    return redirect('cart:cart_detail')

@login_required
def cart_update(request, item_id):  # Renamed from update_cart
    cart_item = get_object_or_404(Cart, id=item_id, user=request.user)
    
    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, "Cart updated successfully.")
        else:
            cart_item.delete()
            messages.success(request, f"{cart_item.product.name} removed from your cart.")
    except ValueError:
        messages.error(request, "Invalid quantity.")
        
    return redirect('cart:cart_detail')