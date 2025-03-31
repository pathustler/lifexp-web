from datetime import timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from LifeXP import settings
from cloudinary.models import CloudinaryField
import datetime
import cloudinary
import cloudinary.uploader
import cloudinary.api
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta
from django.db.models import Sum, F, ExpressionWrapper, IntegerField
from django.db.models.functions import Cast

# from .models import Player

cloudinary.config( 
  cloud_name = settings.CLOUDINARY_STORAGE['CLOUD_NAME'], 
  api_key = settings.CLOUDINARY_STORAGE['API_KEY'], 
  api_secret = settings.CLOUDINARY_STORAGE['API_SECRET'],
  secure = True
)

class PlayerManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if not email:
            raise ValueError("Players must have an email address")
        email = self.normalize_email(email)
        player = self.model(username=username, email=email)
        player.set_password(password)
        player.save(using=self._db)
        return player

    def create_superuser(self, username, email, password):
        return self.create_user(username, email, password)  # No admin access

class Player(AbstractBaseUser):
    def default_xp():
        return {
            "physique": 0,
            "creativity": 0,
            "social": 0,
            "energy": 0,
            "skill": 0
        }

    def default_category_levels():
        return {
            "physique": 1,
            "creativity": 1,
            "social": 1,
            "energy": 1,
            "skill": 1
    }
    
    
    """Custom Player model for site authentication (not for Django admin)"""
    masterytitle_choices = [
        ('Rookie','Rookie'),
        ('Warrior','Warrior'),
        ('Protagonist','Protagonist'),
        ('Diplomat','Diplomat'),
        ('Maverick','Maverick'),
        ('Prodigy','Prodigy')
    ] 
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='player')
    username = models.CharField(max_length=150, unique=True)
    fullname = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(unique=True)
    profile_picture = CloudinaryField('image', blank=True, null=True, default="Screenshot_2025-03-25_at_10.40.01_PM_vugdxk")
    masterytitle = models.CharField( choices=masterytitle_choices, default="Rookie",max_length=150, blank=True, null=True)
    joined_date = models.DateTimeField(default=now)
    lifelevel = models.IntegerField(default=1)
    masterlevel = models.IntegerField(default=1)
    title = models.CharField(max_length=150, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    streak_count = models.IntegerField(default=0)
    last_visit = models.DateField(null=True, blank=True)
    totalxp = models.IntegerField(default=0)
    
    #i want this to be the sum of xp from all the ActivityLog objects related to this user for each category
    categoryxp = models.JSONField(default=default_xp) # A way to store the xp in each category like physique, creativity, social, energy, skill 
    categorylevels = models.JSONField(default=default_category_levels)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Cannot log into admin
    objects = PlayerManager()
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]
    primary_accent_color = models.CharField(max_length=7, default="#555555")
    secondary_accent_color = models.CharField(max_length=7, default="#aaaaaa")
    
    following = models.ManyToManyField(
        "self",  # Self-referential relationship
        symmetrical=False,  # One-way relationship (A follows B, but B doesn't necessarily follow A)
        related_name="followers",
        blank=True
    )
    

    def update_category_xp(self):
        """Recalculate XP for each category and update categoryxp field."""
        from django.apps import apps  # Import inside the method to avoid circular import
        from django.db.models import Sum

        ActivityLog = apps.get_model('main', 'ActivityLog')  # Adjust 'main' to your app name
        Player = apps.get_model('users', 'Player')  # Get the Player model

        # Ensure self.user is a Player instance
        if isinstance(self.user, str):  
            try:
                self.user = Player.objects.get(username=self.user)  # Convert username to Player instance
            except Player.DoesNotExist:
                print("DEBUG: No matching Player found!")
                return  # Stop execution if no player is found

        # Now that self.user is a Player instance, proceed with the query
        xp_data = ActivityLog.objects.filter(user=Player.objects.get(username=self.user))
        xp_distribution = xp_data.aggregate(
            physique_xp=Sum(Cast(F('xp_distribution__physique'), IntegerField())),
            creativity_xp=Sum(Cast(F('xp_distribution__creativity'), IntegerField())),
            social_xp=Sum(Cast(F('xp_distribution__social'), IntegerField())),
            energy_xp=Sum(Cast(F('xp_distribution__energy'), IntegerField())),
            skill_xp=Sum(Cast(F('xp_distribution__skill'), IntegerField()))
        )

        # Construct the category XP dictionary
        self.categoryxp = {
            "physique": xp_distribution['physique_xp'] or 0,
            "creativity": xp_distribution['creativity_xp'] or 0,
            "social": xp_distribution['social_xp'] or 0,
            "energy": xp_distribution['energy_xp'] or 0,
            "skill": xp_distribution['skill_xp'] or 0
        }
        
        
        self.save()
    def follow(self, other_player):
        """Follow another player"""
        if other_player != self:
            self.following.add(other_player)

    def unfollow(self, other_player):
        """Unfollow a player"""
        self.following.remove(other_player)

    def is_following(self, other_player):
        """Check if the player is following another player"""
        return self.following.filter(username=other_player.username).exists()

    def get_followers_count(self):
        """Get the number of followers"""
        return self.followers.count()

    def get_following_count(self):
        """Get the number of players this player is following"""
        return self.following.count()

    def __str__(self):
        return self.username

    def update_streak(self):
        today = now().date()
        
        if self.last_visit == today:
            return  # Already updated today, no change needed
        
        if self.last_visit == today - timedelta(days=1):
            self.streak_count += 1  # Continue streak
        else:
            self.streak_count = 1  # Reset streak to 1 (new start)
        
        self.last_visit = today
        self.save()
    
    def save(self, *args, **kwargs):
        
        max_category = max(self.categoryxp, key=self.categoryxp.get)
        if max(self.categoryxp.values()) < 1000:
            self.masterytitle = "Rookie"
        elif max(self.categoryxp.values()) >= 1000 and max_category == "skill":
            self.masterytitle = "Prodigy"
        elif max(self.categoryxp.values()) >= 1000 and max_category == "physique":
            self.masterytitle = "Warrior"
        elif max(self.categoryxp.values()) >= 1000 and max_category == "creativity":
            self.masterytitle = "Maverick"
        elif max(self.categoryxp.values()) >= 1000 and max_category == "social":
            self.masterytitle = "Diplomat"
        elif max(self.categoryxp.values()) >= 1000 and max_category == "energy":
            self.masterytitle = "Protagonist"

        # Set the primary and secondary accent colors based on mastery title
        primseckey = {
            "Warrior":  ["8D2E2E","EAAFAF"],
            "Protagonist":  ["ECCC00","FDF099"],
            "Diplomat":  ["31784E","AFEAC7"],
            "Maverick":  ["4187A2","AFD9EA"],
            "Prodigy":  ["713599","BAAFEA"],
            "Rookie":  ["555555","AAAAAA"]
        }
        self.primary_accent_color = "#" + primseckey[self.masterytitle][0]
        self.secondary_accent_color = "#" + primseckey[self.masterytitle][1]
      
            
        self.totalxp = sum(self.categoryxp.values())
        self.masterlevel = max(self.categorylevels.values())
        
        # Mastery title should update based on the max value in categoryxp, if max value is less than 600, it should be rookie, if the max value is above 600, and the category with max value is skill, then mastery title would be prodigy and so on
        
        
        super().save(*args, **kwargs)

class SearchHistory(models.Model):
    user = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='search_histories'
    )
    search_query = models.CharField(max_length=255)
    search_type = models.CharField(max_length=50)  # Can be 'user', 'post', 'tag', etc.
    searched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} searched '{self.search_query}' [{self.search_type}]"

class UserSettings(models.Model):
    player = models.OneToOneField(Player, on_delete=models.CASCADE, related_name='settings')
    account_type = models.CharField(max_length=10, choices=[('Private', 'Private'), ('Public', 'Public')], default='Public')
    notifications = models.CharField(max_length=3, choices=[('On', 'On'), ('Off', 'Off')], default='On')
    appearance = models.CharField(max_length=10, choices=[('Light', 'Light'), ('Dark', 'Dark')], default='Light')

    def __str__(self):
        return f"{self.player.username}'s Settings"
    
    
    
    
class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('follow', 'Follow'),
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('message', 'Message'),
        ('system', 'System'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="sent_notifications")
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField(blank=True, null=True)
    related_object_id = models.IntegerField(null=True, blank=True)  # ID of the related object (e.g., post, message)
    created_at = models.DateTimeField(default=now)
    is_read = models.BooleanField(default=False)

    def mark_as_read(self):
        """Marks the notification as read."""
        self.is_read = True
        self.save()

    def __str__(self):
        return f"Notification for {self.recipient.username} - {self.notification_type}"
