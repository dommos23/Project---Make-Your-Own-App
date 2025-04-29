from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

def send_order_confirmation_email(order):
    """Send an email confirmation when an order is placed"""
    subject = f'Order Confirmation - Order #{order.order_number}'
    
    # Create email context
    context = {
        'order': order,
        'order_items': order.items.all(),
        'user': order.user,
    }
    
    # Render email content from template
    email_html_message = render_to_string('orders/email/order_confirmation_email.html', context)
    email_plaintext_message = render_to_string('orders/email/order_confirmation_email.txt', context)
    
    # Send the email
    send_mail(
        subject=subject,
        message=email_plaintext_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.user.email],
        html_message=email_html_message,
        fail_silently=False,
    )

def send_shipping_confirmation_email(order):
    """Send an email confirmation when an order is shipped with tracking info"""
    subject = f'Your Order #{order.order_number} Has Been Shipped!'
    
    # Create email context
    context = {
        'order': order,
        'order_items': order.items.all(),
        'user': order.user,
        'tracking_number': order.tracking_number,
        'carrier': order.carrier,
        'shipping_date': order.shipping_date,
    }
    
    # Render email content from template
    email_html_message = render_to_string('orders/email/shipping_confirmation_email.html', context)
    email_plaintext_message = render_to_string('orders/email/shipping_confirmation_email.txt', context)
    
    # Send the email
    send_mail(
        subject=subject,
        message=email_plaintext_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.user.email],
        html_message=email_html_message,
        fail_silently=False,
    )