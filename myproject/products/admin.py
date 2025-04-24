# products/admin.py
from django.contrib import admin
from .models import Product, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock', 'category', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['price', 'stock']  # Allow quick editing of stock levels
    
    # Add a custom filter for low stock products
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.GET.get('low_stock'):
            return qs.filter(stock__lt=5)
        return qs
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['low_stock_count'] = Product.objects.filter(stock__lt=5).count()
        return super().changelist_view(request, extra_context=extra_context)