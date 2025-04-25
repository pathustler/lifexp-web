from django.db.models.signals import post_save,post_delete
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Player, UserSettings
from django.apps import apps


# @receiver(post_save, sender=apps.get_model('main', 'ActivityLog'))
# @receiver(post_delete, sender=apps.get_model('main', 'ActivityLog'))
# def update_user_xp(sender, instance, **kwargs):
#     if hasattr(instance.user, 'userprofile'):  # Ensure the user has a profile
#         instance.user.userprofile.update_category_xp()
        
        

@receiver(post_save, sender=Player)
def create_user_settings(sender, instance, created, **kwargs):
    if created:
        UserSettings.objects.create(player=instance)