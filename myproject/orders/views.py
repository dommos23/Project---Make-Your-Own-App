# orders/views.py - Clean up imports
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Order, OrderItem
from discounts.forms import DiscountApplyForm
from discounts.models import Discount
from .utils import send_order_confirmation_email
import re
import uuid
from caRT.models import Cart
from .forms import OrderCreateForm
from payments.forms import PaymentForm
@login_required
def order_history(request): 
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
def order_cancel(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Only allow cancellation of pending orders
    if order.status != 'Pending':
        messages.error(request, "Only pending orders can be cancelled.")
        return redirect('orders:order_detail', order_id=order.id)
    
    if request.method == 'POST':
        # Update order status
        order.status = 'Cancelled'
        order.save()
        
        # Restore product quantities
        for item in order.items.all():
            product = item.product
            product.stock += item.quantity
            product.save()
        
        messages.success(request, "Your order has been cancelled and product quantities have been restored.")
        return redirect('orders:order_history')
    
    # If not POST request, redirect back to order detail
    return redirect('orders:order_detail', order_id=order.id)
@login_required
def order_create(request):
    cart_items = Cart.objects.filter(user=request.user)
    
    if not cart_items:
        messages.warning(request, "Your cart is empty.")
        return redirect('caRT:cart_detail')
    
    if request.method == 'POST':
        order_form = OrderCreateForm(request.POST)
        payment_form = PaymentForm(request.POST)
        
        # Validate credit card information
        card_number = request.POST.get('card_number', '')
        card_expiry = request.POST.get('card_expiry', '')
        card_cvv = request.POST.get('card_cvv', '')
        
        # Custom validation
        is_valid = True
        if not re.match(r'^[0-9]{13,16}$', card_number):
            messages.error(request, "Please enter a valid card number (13-16 digits).")
            is_valid = False
        
        if not re.match(r'^(0[1-9]|1[0-2])\/[0-9]{2}$', card_expiry):
            messages.error(request, "Please enter a valid expiration date in MM/YY format.")
            is_valid = False
        
        if not re.match(r'^[0-9]{3,4}$', card_cvv):
            messages.error(request, "Please enter a valid CVV (3-4 digits).")
            is_valid = False
        
        if order_form.is_valid() and payment_form.is_valid() and is_valid:
            # Create order
            order = order_form.save(commit=False)
            order.user = request.user
            
            # Calculate total price from cart
            total_price = sum(item.get_total_price() for item in cart_items)
            
            # Apply discount if available
            discount_code = request.session.get('discount_code')
            if discount_code:
                try:
                    discount = Discount.objects.get(code=discount_code)
                    if discount.is_valid(total_price):
                        discount_amount = discount.get_discount_amount(total_price)
                        order.discount = discount
                        order.discount_amount = discount_amount
                        total_price -= discount_amount
                        
                        # Increment usage count
                        discount.current_usage += 1
                        discount.save()
                        
                        # Clear discount from session
                        del request.session['discount_code']
                except Discount.DoesNotExist:
                    pass
            
            order.total_price = total_price
            order.save()
            
            # Create order items
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
            
            # Process payment
            payment = payment_form.save(commit=False)
            payment.user = request.user
            payment.order = order
            payment.amount = total_price
            payment.status = 'Completed'
            # Store card info (in a real app, you'd store a token, not actual card details)
            payment.transaction_id = f"TRANS-{uuid.uuid4().hex[:8].upper()}"
            payment.save()
            
            # Update order status
            order.status = 'Paid'
            order.save()
            
            # Decrease product quantities
            for item in order.items.all():
                product = item.product
                product.stock -= item.quantity
                product.save()
            
            # Clear the cart
            cart_items.delete()
            # After the order is created and processed (after order.save() and before the redirect)
            try:
            # Send order confirmation email
                send_order_confirmation_email(order)
            except Exception as e:
    # Log the error but don't stop the process
                print(f"Error sending order confirmation email: {str(e)}")
            messages.success(request, "Your order has been placed and payment processed successfully.")
            return redirect('orders:order_detail', order_id=order.id)
        # After the order is created and processed (after order.save() and before the redirect)
        messages.success(request, "Your order has been placed and payment processed successfully.")
        return redirect('orders:order_detail', order_id=order.id)
    else:
        order_form = OrderCreateForm()
        payment_form = PaymentForm(initial={'payment_method': 'Credit Card'})
    
    context = {
        'order_form': order_form,
        'payment_form': payment_form,
        'cart_items': cart_items,
        'cart_total': sum(item.get_total_price() for item in cart_items)
    }
    
    return render(request, 'orders/order_create.html', context)