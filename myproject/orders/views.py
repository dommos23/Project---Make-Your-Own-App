from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Order, OrderItem
from .forms import OrderCreateForm
from caRT.models import Cart
from payments.forms import PaymentForm

from payments.forms import PaymentForm
@login_required
def order_history(request):  # Renamed from order_list
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    orders_count = orders.count()
    return render(request, 'orders/order_history.html', {
        'orders': orders,
        'orders_count': orders_count
    })

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})

@login_required
def order_create(request):
    cart_items = Cart.objects.filter(user=request.user)
    
    if not cart_items:
        messages.warning(request, "Your cart is empty.")
        return redirect('cart:cart_detail')
    
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            
            # Calculate total price from cart
            total_price = sum(item.get_total_price() for item in cart_items)
            order.total_price = total_price
            order.save()
            
            # Create order items from cart
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
            
            # Clear the cart
            cart_items.delete()
            
            messages.success(request, "Your order has been placed successfully.")
            return redirect('payments:payment_process')  # Forward to payment
    else:
        form = OrderCreateForm()
    
    context = {
        'shipping_form': form,  # Renamed to match template
        'cart_items': cart_items,
        'cart_total': sum(item.get_total_price() for item in cart_items),
        'payment_form': PaymentForm()  # Added to match template
    }
    
    return render(request, 'orders/order_create.html', context)