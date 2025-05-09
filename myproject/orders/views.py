from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Order, OrderItem
from payments.models import SavedPaymentMethod
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
    user = request.user
    has_profile_address = hasattr(user, 'profile') and user.profile.address
    
    if not cart_items:
        messages.warning(request, "Your cart is empty.")
        return redirect('caRT:cart_detail')
    
    # Calculate cart total
    cart_total = sum(item.get_total_price() for item in cart_items)
    
    # Get discount information from session
    discount_code = request.session.get('discount_code')
    discount = None
    discount_amount = 0
    final_total = cart_total
    
    if discount_code:
        try:
            from discounts.models import Discount
            discount = Discount.objects.get(code=discount_code)
            if discount.is_valid(cart_total):
                discount_amount = discount.get_discount_amount(cart_total)
                final_total = cart_total - discount_amount
            else:
                # Invalid discount
                discount = None
                del request.session['discount_code']
        except (ImportError, Discount.DoesNotExist):
            # No discount model or discount not found
            discount = None
            if 'discount_code' in request.session:
                del request.session['discount_code']
                
    saved_payment_methods = SavedPaymentMethod.objects.filter(user=request.user)
    default_payment_method = saved_payment_methods.filter(is_default=True).first()
    
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
            
        use_saved_method = request.POST.get('use_saved_method')
        if use_saved_method and use_saved_method.isdigit():
            saved_method_id = int(use_saved_method)
            try:
                saved_method = SavedPaymentMethod.objects.get(id=saved_method_id, user=request.user)
                # Use the saved method (in a real implementation, you'd retrieve the actual card data from a secure storage)
                # Here we're just using the payment method type
                payment_form.instance.payment_method = saved_method.payment_method
                # Skip card validation since we're using a saved method
                is_valid = True
            except SavedPaymentMethod.DoesNotExist:
                messages.error(request, "Selected payment method not found.")
                is_valid = False
                
        if order_form.is_valid() and payment_form.is_valid() and is_valid:
            # Create order
            order = order_form.save(commit=False)
            order.user = request.user
            
            # Check if user wants to use profile address
            use_profile_address = order_form.cleaned_data.get('use_profile_address')
            if use_profile_address and has_profile_address:
                # Copy address from profile
                profile = user.profile
                order.shipping_address = profile.address
                order.shipping_city = profile.city
                order.shipping_state = profile.state
                order.shipping_zip = profile.zip_code
                order.shipping_country = profile.country
                
                # Log to verify this is happening
                print(f"Using profile address: {profile.address}, {profile.city}, {profile.state}")
            else:
                print("Using form address")
                
            save_payment_method = payment_form.cleaned_data.get('save_payment_method')
            if save_payment_method and not use_saved_method:
                # Only save if using a new payment method
                card_number = request.POST.get('card_number', '')
                card_expiry = request.POST.get('card_expiry', '')
                
                # Save the payment method (only store last 4 digits of card)
                SavedPaymentMethod.objects.create(
                    user=request.user,
                    payment_method=payment_form.cleaned_data['payment_method'],
                    card_last_digits=card_number[-4:] if card_number else '',
                    card_expiry=card_expiry,
                    is_default=not SavedPaymentMethod.objects.filter(user=request.user).exists()  # Make default if first
                )
            
            # Apply the discount (if any)
            if discount:
                order.discount = discount
                order.discount_amount = discount_amount
                order.total_price = final_total
                # Increment usage
                discount.current_usage += 1
                discount.save()
                # Clear from session
                if 'discount_code' in request.session:
                    del request.session['discount_code']
            else:
                order.total_price = cart_total
            
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
            payment.amount = order.total_price
            payment.status = 'Completed'
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
            
            # Send order confirmation email (if implemented)
            try:
                from .utils import send_order_confirmation_email
                send_order_confirmation_email(order)
            except Exception as e:
                print(f"Error sending confirmation email: {str(e)}")
            
            messages.success(request, "Your order has been placed and payment processed successfully.")
            return redirect('orders:order_detail', order_id=order.id)
    else:
        order_form = OrderCreateForm()
        
        # If user has a default payment method, pre-select it
        initial_payment_data = {'payment_method': 'Credit Card'}
        if default_payment_method:
            initial_payment_data['payment_method'] = default_payment_method.payment_method
        
        payment_form = PaymentForm(initial=initial_payment_data)
    
    context = {
        'order_form': order_form,
        'payment_form': payment_form,
        'cart_items': cart_items,
        'cart_total': cart_total,
        'discount': discount,
        'discount_amount': discount_amount,
        'final_total': final_total,
        'saved_payment_methods': saved_payment_methods,
        'default_payment_method': default_payment_method,
        'has_profile_address': has_profile_address,  # Add this line
    }
    
    return render(request, 'orders/order_create.html', context)