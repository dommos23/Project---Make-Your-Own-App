# two_factor/apps.py
from django.apps import AppConfig

class TwoFactorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'two_factor'

    def ready(self):
        import two_factor.signals  # Import signals