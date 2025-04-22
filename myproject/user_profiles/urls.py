from django.urls import path
from . import views

app_name = 'user_profiles'

urlpatterns = [
    path('', views.profile_view, name='profile'),
    path('edit/', views.profile_edit, name='profile_edit'),
    path('addresses/', views.address_list, name='address_list'),
    path('addresses/add/', views.address_add, name='address_add'),
    path('addresses/edit/<int:address_id>/', views.address_edit, name='address_edit'),
    path('addresses/delete/<int:address_id>/', views.address_delete, name='address_delete'),
]