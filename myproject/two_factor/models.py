# two_factor/models.py
from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone
from datetime import timedelta

class UserTwoFactorSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='two_factor_settings')
    is_enabled = models.BooleanField(default=False)
    
    def __str__(self):
        return f"2FA settings for {self.user.username}"

class EmailVerificationCode(models.Model):
    # Keep the existing model as-is
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Verification code for {self.user.username}"
    
    def save(self, *args, **kwargs):
        # Set expiration time to 10 minutes from now
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    @classmethod
    def generate_code(cls, user):
        # Generate a random 6-digit code
        import random
        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        # Create and return a new verification code
        return cls.objects.create(
            user=user,
            code=code,
        )