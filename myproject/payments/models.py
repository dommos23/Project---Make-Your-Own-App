# payments/models.py
from django.db import models
from django.contrib.auth.models import User
from orders.models import Order

class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
        ('Refunded', 'Refunded'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('Credit Card', 'Credit Card'),
        ('PayPal', 'PayPal'),
        ('Bank Transfer', 'Bank Transfer'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
class SavedPaymentMethod(models.Model):
        PAYMENT_METHOD_CHOICES = [
        ('Credit Card', 'Credit Card'),
        ('PayPal', 'PayPal'),
        ('Bank Transfer', 'Bank Transfer'),
        ]
    
        user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_methods')
        payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
        card_last_digits = models.CharField(max_length=4, blank=True)
        card_expiry = models.CharField(max_length=5, blank=True)  # MM/YY
        is_default = models.BooleanField(default=False)
        created_at = models.DateTimeField(auto_now_add=True)
    
def __str__(self):
        if self.payment_method == 'Credit Card':
            return f"Credit Card ending in {self.card_last_digits}"
        return self.payment_method
    
def save(self, *args, **kwargs):
        # If this is set as default, unset any other defaults
        if self.is_default:
            SavedPaymentMethod.objects.filter(
                user=self.user, 
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
    
def __str__(self):
        return f"Payment {self.id} for Order {self.order.order_number}"