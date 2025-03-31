from django.db.models.signals import post_save,post_delete
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Player
from django.apps import apps
from .models import UserProfile  # Import only UserProfile to avoid circular imports

@receiver(post_save, sender=apps.get_model('main', 'ActivityLog'))
@receiver(post_delete, sender=apps.get_model('main', 'ActivityLog'))
def update_user_xp(sender, instance, **kwargs):
    if hasattr(instance.user, 'userprofile'):  # Ensure the user has a profile
        instance.user.userprofile.update_category_xp()
        
        

