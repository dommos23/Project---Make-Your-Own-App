# two_factor/urls.py
from django.urls import path
from . import views

app_name = 'two_factor'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('verify/', views.verify_code, name='verify'),
    path('settings/', views.two_factor_settings, name='settings'),  # New URL
]