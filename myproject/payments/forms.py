# payments/forms.py
from django import forms
from .models import Payment

class PaymentForm(forms.ModelForm):
    card_number = forms.CharField(max_length=16, required=True, widget=forms.TextInput(attrs={'placeholder': 'Card Number'}))
    card_expiry = forms.CharField(max_length=5, required=True, widget=forms.TextInput(attrs={'placeholder': 'MM/YY'}))
    card_cvv = forms.CharField(max_length=4, required=True, widget=forms.TextInput(attrs={'placeholder': 'CVV'}))
    
    class Meta:
        model = Payment
        fields = ['payment_method']
        
    def clean(self):
        # This is where you would typically validate the card details
        # For a real app, you'd use a payment processor API instead
        cleaned_data = super().clean()
        return cleaned_data