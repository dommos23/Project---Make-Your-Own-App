# discounts/forms.py
from django import forms
from .models import Discount

class DiscountApplyForm(forms.Form):
    code = forms.CharField(label='Promo Code', max_length=50, required=False,
                         widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter promo code'}))