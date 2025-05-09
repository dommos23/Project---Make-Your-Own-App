# Add these imports to the top of your views.py files as needed

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from payments.models import SavedPaymentMethod
from .models import Payment
from .forms import PaymentForm
from orders.models import Order

@login_required
def payment_process(request):
    # Get the user's most recent pending order
    try:
        order = Order.objects.filter(user=request.user, status='Pending').latest('created_at')
    except Order.DoesNotExist:
        messages.warning(request, "No pending orders found.")
        return redirect('orders:order_history')
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            # In a real app, you would process payment through a payment gateway here
            payment = form.save(commit=False)
            payment.user = request.user
            payment.order = order
            payment.amount = order.total_price
            payment.status = 'Completed'  # For demo purposes
            payment.save()
            
            # Update order status
            order.status = 'Paid'
            order.save()
            
            # Decrease product quantities
            for item in order.items.all():
                product = item.product
                product.stock -= item.quantity
                product.save()
            
            messages.success(request, "Payment successful!")
            return redirect('payments:payment_success')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PaymentForm(initial={'payment_method': 'Credit Card'})
    
    return render(request, 'payments/payment_process.html', {
        'order': order,
        'form': form,
    })
# payments/views.py
@login_required
def manage_payment_methods(request):
    payment_methods = SavedPaymentMethod.objects.filter(user=request.user)
    
    if request.method == 'POST':
        if 'set_default' in request.POST:
            method_id = request.POST.get('set_default')
            try:
                method = SavedPaymentMethod.objects.get(id=method_id, user=request.user)
                method.is_default = True
                method.save()
                messages.success(request, "Default payment method updated.")
            except SavedPaymentMethod.DoesNotExist:
                messages.error(request, "Payment method not found.")
        
        elif 'delete_method' in request.POST:
            method_id = request.POST.get('delete_method')
            try:
                method = SavedPaymentMethod.objects.get(id=method_id, user=request.user)
                method.delete()
                messages.success(request, "Payment method removed.")
            except SavedPaymentMethod.DoesNotExist:
                messages.error(request, "Payment method not found.")
        
        return redirect('payments:manage_methods')
    
    return render(request, 'payments/manage_methods.html', {
        'payment_methods': payment_methods
    })
@login_required
def payment_success(request):
    # Get the user's most recent paid order
    try:
        order = Order.objects.filter(user=request.user, status='Paid').latest('created_at')
    except Order.DoesNotExist:
        messages.warning(request, "No paid orders found.")
        return redirect('orders:order_history')
    
    return render(request, 'payments/payment_success.html', {
        'order': order,
        'user': request.user
    })

@login_required
def payment_cancel(request):  # Renamed from payment_failed
    return render(request, 'payments/payment_cancel.html')