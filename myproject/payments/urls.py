from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('process/', views.payment_process, name='payment_process'),
    path('success/', views.payment_success, name='payment_success'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
]