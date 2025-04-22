from django import forms
from .models import Order

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['shipping_address', 'shipping_city', 'shipping_state', 
                 'shipping_zip', 'shipping_country']
        widgets = {
            'shipping_address': forms.Textarea(attrs={'rows': 3}),
        }