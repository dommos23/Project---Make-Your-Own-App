from django import forms
from .models import Payment

class PaymentForm(forms.ModelForm):
    card_number = forms.CharField(max_length=16, required=True, 
                                 widget=forms.TextInput(attrs={'placeholder': 'Card Number'}))
    card_expiry = forms.CharField(max_length=5, required=True, 
                                 widget=forms.TextInput(attrs={'placeholder': 'MM/YY'}))
    card_cvv = forms.CharField(max_length=4, required=True, 
                              widget=forms.TextInput(attrs={'placeholder': 'CVV'}))
    
    class Meta:
        model = Payment
        fields = ['payment_method']
        
    def clean_card_number(self):
        card_number = self.cleaned_data.get('card_number')
        # Basic validation - in a real app you'd use a payment processing library
        if not card_number.isdigit() or len(card_number) < 13 or len(card_number) > 16:
            raise forms.ValidationError("Please enter a valid card number")
        return card_number
        
    def clean_card_expiry(self):
        card_expiry = self.cleaned_data.get('card_expiry')
        # Check if expiry date is in MM/YY format
        if len(card_expiry) != 5 or card_expiry[2] != '/':
            raise forms.ValidationError("Please enter expiry date in MM/YY format")
        return card_expiry
        
    def clean_card_cvv(self):
        card_cvv = self.cleaned_data.get('card_cvv')
        if not card_cvv.isdigit() or len(card_cvv) < 3 or len(card_cvv) > 4:
            raise forms.ValidationError("Please enter a valid CVV")
        return card_cvv