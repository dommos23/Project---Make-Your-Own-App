# Add these imports to the top of your views.py files as needed
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cart
from products.models import Product
from discounts.forms import DiscountApplyForm
from discounts.models import Discount
# Remove any unnecessary imports
@login_required
def cart_detail(request):
    cart_items = Cart.objects.filter(user=request.user)
    cart_total = sum(item.get_total_price() for item in cart_items)
    
    # Get current discount from session
    discount_code = request.session.get('discount_code')
    discount = None
    discount_amount = 0
    
    if discount_code:
        try:
            discount = Discount.objects.get(code=discount_code)
            if discount.is_valid(cart_total):
                discount_amount = discount.get_discount_amount(cart_total)
            else:
                # Invalid discount, remove from session
                del request.session['discount_code']
                messages.warning(request, "The discount code is not valid anymore.")
        except Discount.DoesNotExist:
            # Discount not found, remove from session
            del request.session['discount_code']
    
    # Apply discount form
    if request.method == 'POST':
        form = DiscountApplyForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            if code:
                try:
                    discount = Discount.objects.get(code=code)
                    if discount.is_valid(cart_total):
                        request.session['discount_code'] = code
                        discount_amount = discount.get_discount_amount(cart_total)
                        messages.success(request, "Discount applied successfully!")
                    else:
                        messages.warning(request, "This discount code is not valid.")
                except Discount.DoesNotExist:
                    messages.warning(request, "Invalid discount code.")
            else:
                # No code provided, remove discount
                if 'discount_code' in request.session:
                    del request.session['discount_code']
                    messages.info(request, "Discount removed.")
            
            return redirect('caRT:cart_detail')
    else:
        form = DiscountApplyForm()
    
    context = {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'discount_form': form,
        'discount': discount,
        'discount_amount': discount_amount,
        'final_total': cart_total - discount_amount
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
        cart_item.quantity = quantity  # Instead of += quantity
        cart_item.save()
    
    messages.success(request, f"{product.name} added to your cart.")
    return redirect('caRT:cart_detail')

@login_required
def cart_remove(request, item_id):  # Renamed from remove_from_cart
    cart_item = get_object_or_404(Cart, id=item_id, user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    
    messages.success(request, f"{product_name} removed from your cart.")
    return redirect('caRT:cart_detail')


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
        
    return redirect('caRT:cart_detail')
