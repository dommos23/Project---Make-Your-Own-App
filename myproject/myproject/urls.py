from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import home_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),  # Keep only one home view
    path('products/', include('products.urls')),
    path('cart/', include('caRT.urls')),
    path('orders/', include('orders.urls')),
    path('auth/', include('two_factor.urls')),  # Change to a more specific path
    path('accounts/', include('allauth.urls')),
    path('profile/', include('user_profiles.urls')),
    path('payments/', include('payments.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)