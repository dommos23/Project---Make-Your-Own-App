from django.contrib import admin
from .models import Order, OrderItem
from .utils import send_shipping_confirmation_email
from django.contrib import messages

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    readonly_fields = ['price']
    extra = 0
    
def mark_as_shipped(modeladmin, request, queryset):
    from django.utils import timezone
    today = timezone.now().date()
    
    for order in queryset:
        if order.status == 'Paid':
            order.status = 'Shipped'
            if not order.shipping_date:
                order.shipping_date = today
            order.save()
             # Send shipping confirmation email
            try:
                send_shipping_confirmation_email(order)
            except Exception as e:
                messages.error(request, f"Error sending shipping email for order #{order.order_number}: {str(e)}")


mark_as_shipped.short_description = "Mark selected orders as shipped and send confirmation emails"

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'order_number', 'user', 'status', 'total_price', 'created_at', 'tracking_number']
    list_filter = ['status', 'created_at', 'shipping_date']
    search_fields = ['order_number', 'user__username', 'user__email', 'tracking_number']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'total_price', 'created_at', 'updated_at')
        }),
        ('Shipping Details', {
            'fields': ('shipping_address', 'shipping_city', 'shipping_state', 'shipping_zip', 'shipping_country')
        }),
        ('Tracking Information', {
            'fields': ('tracking_number', 'carrier', 'shipping_date'),
            'classes': ('collapse',),
        }),
    )
    actions = [mark_as_shipped]
    
    def get_readonly_fields(self, request, obj=None):
        # Make more fields readonly after order is paid
        if obj and obj.status != 'Pending':
            return self.readonly_fields + ['user', 'shipping_address', 'shipping_city', 
                                          'shipping_state', 'shipping_zip', 'shipping_country']
        return self.readonly_fields
    
    def save_model(self, request, obj, form, change):
        # When status changes to "Shipped", set shipping date if not already set
        if change and 'status' in form.changed_data and obj.status == 'Shipped' and not obj.shipping_date:
            from django.utils import timezone
            obj.shipping_date = timezone.now().date()
        super().save_model(request, obj, form, change)
          # Send shipping confirmation email
        try:
                send_shipping_confirmation_email(obj)
        except Exception as e:
                # Log the error
                print(f"Error sending shipping confirmation email: {str(e)}")
                messages.error(request, f"Error sending shipping confirmation email: {str(e)}")
        else:
            super().save_model(request, obj, form, change)