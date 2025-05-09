# user_profiles/management/commands/create_user_profiles.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from user_profiles.models import UserProfile

class Command(BaseCommand):
    help = 'Creates UserProfile objects for users without profiles'

    def handle(self, *args, **options):
        users_without_profiles = []
        
        for user in User.objects.all():
            try:
                # Access profile to see if it exists
                profile = user.profile
            except:
                # Create profile if it doesn't exist
                UserProfile.objects.create(user=user)
                users_without_profiles.append(user.username)
        
        if users_without_profiles:
            self.stdout.write(self.style.SUCCESS(f'Created profiles for users: {", ".join(users_without_profiles)}'))
        else:
            self.stdout.write(self.style.SUCCESS('All users already have profiles.'))