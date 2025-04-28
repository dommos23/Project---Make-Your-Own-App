# Add these imports to the top of your views.py files as needed
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserProfileForm, UserForm
from orders.models import Order

@login_required
def profile_view(request):
    user = request.user
    profile = user.profile  # Add this line to get the profile
    orders_count = Order.objects.filter(user=user).count()
    
    return render(request, 'user_profiles/profile.html', {
        'user': user,
        'profile': profile,  # Add this to the context
        'orders_count': orders_count
    })

@login_required
def profile_edit(request):  # Renamed from edit_profile
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, instance=request.user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile was successfully updated.")
            return redirect('user_profiles:profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    
    return render(request, 'user_profiles/profile_edit.html', context)

# New address management views
@login_required
def address_list(request):
    # Assuming addresses are stored in the UserProfile model
    user = request.user
    return render(request, 'user_profiles/address_list.html', {'user': user})

@login_required
def address_add(request):
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, instance=request.user.profile)
        
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Address added successfully.")
            return redirect('user_profiles:address_list')
    else:
        profile_form = UserProfileForm(instance=request.user.profile)
    
    return render(request, 'user_profiles/address_add.html', {'form': profile_form})

@login_required
def address_edit(request, address_id):
    # Since we're using the UserProfile model for addresses, address_id isn't used
    # but keeping parameter for consistency with URL pattern
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, instance=request.user.profile)
        
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Address updated successfully.")
            return redirect('user_profiles:address_list')
    else:
        profile_form = UserProfileForm(instance=request.user.profile)
    
    return render(request, 'user_profiles/address_edit.html', {'form': profile_form})

@login_required
def address_delete(request, address_id):
    # Since we're using UserProfile for addresses, we'll just clear the fields
    # but keeping parameter for consistency with URL pattern
    profile = request.user.profile
    profile.address = ''
    profile.city = ''
    profile.state = ''
    profile.zip_code = ''
    profile.country = ''
    profile.save()
    
    messages.success(request, "Address deleted successfully.")
    return redirect('user_profiles:address_list')