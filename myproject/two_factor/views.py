from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import EmailVerificationCode, UserTwoFactorSettings
from .forms import VerificationCodeForm, TwoFactorSettingsForm

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('login')
        password = request.POST.get('password')
        
        # Check if username is actually an email
        if '@' in username:
            from django.contrib.auth.models import User
            try:
                # Change this line to filter instead of get
                user_objs = User.objects.filter(email=username)
                if user_objs.exists():
                    # Use the first user with this email
                    user_obj = user_objs.first()
                    username = user_obj.username
                else:
                    messages.error(request, "Invalid email or password.")
                    return redirect('two_factor:login')
            except Exception as e:
                messages.error(request, f"Login error: {str(e)}")
                return redirect('two_factor:login')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if 2FA is enabled for this user
            try:
                two_factor_settings = UserTwoFactorSettings.objects.get(user=user)
                if two_factor_settings.is_enabled:
                    # Generate verification code
                    verification = EmailVerificationCode.generate_code(user)
                    
                    # Store user ID in session for the verification step
                    request.session['user_id_to_verify'] = user.id
                    
                    # Send verification code via email
                    send_verification_email(user, verification.code)
                    
                    # Redirect to verification page
                    return redirect('two_factor:verify')
                else:
                    # If 2FA is disabled, log in directly
                    login(request, user)
                    messages.success(request, "Successfully logged in.")
                    return redirect('home')
            except UserTwoFactorSettings.DoesNotExist:
                # If settings don't exist, create them and log in
                UserTwoFactorSettings.objects.create(user=user, is_enabled=False)
                login(request, user)
                messages.success(request, "Successfully logged in.")
                return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, 'two_factor/login.html')

def verify_code(request):
    user_id = request.session.get('user_id_to_verify')
    
    if not user_id:
        messages.error(request, "Please log in first.")
        return redirect('two_factor:login')
    
    if request.method == 'POST':
        form = VerificationCodeForm(request.POST)
        
        if form.is_valid():
            code = form.cleaned_data['code']
            
            try:
                from django.contrib.auth.models import User
                from django.contrib.auth import login
                user = User.objects.get(id=user_id)
                verification = EmailVerificationCode.objects.filter(
                    user=user,
                    code=code,
                    is_used=False,
                    expires_at__gt=timezone.now()
                ).latest('created_at')
                
                # Mark code as used
                verification.is_used = True
                verification.save()
                
                # Log the user in - specify the backend
                from django.contrib.auth import authenticate
                # This re-authenticates the user with the default backend
                authenticated_user = authenticate(username=user.username, password=None, backend='django.contrib.auth.backends.ModelBackend')
                if authenticated_user is None:
                    # If that fails, manually set the backend
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    login(request, user)
                else:
                    login(request, authenticated_user)
                
                # Clear session data
                if 'user_id_to_verify' in request.session:
                    del request.session['user_id_to_verify']
                
                messages.success(request, "Successfully logged in.")
                return redirect('home')
                
            except (User.DoesNotExist, EmailVerificationCode.DoesNotExist):
                messages.error(request, "Invalid or expired verification code.")
        
    else:
        form = VerificationCodeForm()
    
    return render(request, 'two_factor/verify.html', {'form': form})

@login_required
def two_factor_settings(request):
    try:
        settings = UserTwoFactorSettings.objects.get(user=request.user)
    except UserTwoFactorSettings.DoesNotExist:
        settings = UserTwoFactorSettings.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = TwoFactorSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, "Two-factor authentication settings updated successfully.")
            return redirect('two_factor:settings')
    else:
        form = TwoFactorSettingsForm(instance=settings)
    
    return render(request, 'two_factor/settings.html', {'form': form})

def send_verification_email(user, code):
    subject = 'Your Login Verification Code'
    message = f'Your verification code is: {code}\n\nThis code will expire in 10 minutes.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]
    
    send_mail(
        subject,
        message,
        from_email,
        recipient_list,
        fail_silently=False,
    )