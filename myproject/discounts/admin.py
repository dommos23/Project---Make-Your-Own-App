# discounts/admin.py
from django.contrib import admin
from .models import Discount

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'value', 'valid_from', 'valid_to', 'current_usage', 'active']
    list_filter = ['active', 'discount_type', 'valid_from', 'valid_to']
    search_fields = ['code', 'description']
    filter_horizontal = ['products', 'categories']
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'description', 'active')
        }),
        ('Discount Details', {
            'fields': ('discount_type', 'value', 'products', 'categories')
        }),
        ('Validity', {
            'fields': ('valid_from', 'valid_to', 'usage_limit', 'current_usage', 'min_order_value')
        }),
    )