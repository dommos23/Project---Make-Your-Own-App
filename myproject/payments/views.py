# Add these imports to the top of your views.py files as needed

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
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
            payment = form.save(commit=False)
            payment.user = request.user
            payment.order = order
            payment.amount = order.total_price
            payment.status = 'Completed'  # For demo, assume payment is successful
            payment.save()
            
            # Update order status
            order.status = 'Paid'
            order.save()
            
            messages.success(request, "Payment successful!")
            return redirect('payments:payment_success')
    else:
        form = PaymentForm(initial={'payment_method': 'Credit Card'})
    
    return render(request, 'payments/payment_process.html', {
        'order': order,
        'form': form,
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