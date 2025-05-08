from django import forms
from .models import Order

class OrderCreateForm(forms.ModelForm):
    use_profile_address = forms.BooleanField(
        required=False,
        initial=False,
        label="Use my profile address",
        help_text="Check this to use the address from your profile"
    )
    
    class Meta:
        model = Order
        fields = ['shipping_address', 'shipping_city', 'shipping_state', 
                 'shipping_zip', 'shipping_country']
        widgets = {
            'shipping_address': forms.Textarea(attrs={'rows': 3}),
        }