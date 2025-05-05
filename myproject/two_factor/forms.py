# two_factor/forms.py
from django import forms
from .models import UserTwoFactorSettings

class VerificationCodeForm(forms.Form):
    # Keep your existing VerificationCodeForm
    code = forms.CharField(
        max_length=6, 
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter 6-digit code'
        })
    )

class TwoFactorSettingsForm(forms.ModelForm):
    class Meta:
        model = UserTwoFactorSettings
        fields = ['is_enabled']
        labels = {
            'is_enabled': 'Enable two-factor authentication'
        }
        help_texts = {
            'is_enabled': 'When enabled, you will be asked to enter a verification code sent to your email when logging in.'
        }