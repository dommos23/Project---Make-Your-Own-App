# discounts/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from products.models import Product, Category

class Discount(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]
    
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Optional relationships for specific products or categories
    products = models.ManyToManyField(Product, blank=True)
    categories = models.ManyToManyField(Category, blank=True)
    
    # Validity period
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField(blank=True, null=True)
    
    # Usage limits
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    current_usage = models.PositiveIntegerField(default=0)
    
    # Minimum order value
    min_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Is active
    active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.code
    
    def is_valid(self, cart_total=None):
        now = timezone.now()
        
        # Check time validity
        if self.valid_to and now > self.valid_to:
            return False
        if now < self.valid_from:
            return False
        
        # Check usage limit
        if self.usage_limit and self.current_usage >= self.usage_limit:
            return False
        
        # Check minimum order value
        if cart_total and cart_total < self.min_order_value:
            return False
        
        return self.active
    
    def get_discount_amount(self, total):
        if self.discount_type == 'percentage':
            # Ensure percentage is valid
            percentage = min(max(self.value, 0), 100)
            return (total * percentage) / 100
        else:  # fixed amount
            return min(self.value, total)  # Don't discount more than the total