from datetime import timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from LifeXP import settings
from cloudinary.models import CloudinaryField
import datetime
import cloudinary
import cloudinary.uploader
import cloudinary.api
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
    
    username = models.CharField(max_length=150, unique=True)
    fullname = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(unique=True)
    profile_picture = CloudinaryField('image', blank=True, null=True) # Use cloudinary for better media management
    masterytitle = models.CharField( choices=masterytitle_choices, default="Rookie",max_length=150, blank=True, null=True)
    lifelevel = models.IntegerField(default=1)
    masterlevel = models.IntegerField(default=1)
    title = models.CharField(max_length=150, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    streak_count = models.IntegerField(default=0)
    totalxp = models.IntegerField(default=0)
    categoryxp = models.JSONField(default=default_xp) # A way to store the xp in each category like physique, creativity, social, energy, skill 
    categorylevels = models.JSONField(default=default_category_levels)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Cannot log into admin
    objects = PlayerManager()
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]
    primary_accent_color = models.CharField(max_length=7, default="#555555")
    secondary_accent_color = models.CharField(max_length=7, default="#aaaaaa")

    def __str__(self):
        return self.username
    
    def save(self, *args, **kwargs):
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
