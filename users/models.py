from datetime import timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from LifeXP import settings
from cloudinary.models import CloudinaryField
import datetime
import cloudinary
import cloudinary.uploader
import cloudinary.api

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
    # profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
    profile_picture = CloudinaryField('image', blank=True, null=True) # Use cloudinary for better media management

    masterytitle = models.CharField( choices=masterytitle_choices, default="Rookie",max_length=150, blank=True, null=True)
    # Gamified fields

    lifelevel = models.IntegerField(default=1)
    masterlevel = models.IntegerField(default=1)
    title = models.CharField(max_length=150, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)


    streak_count = models.IntegerField(default=0)
    
    # A way to store the xp in each category like physique, creativity, social, energy, skill 
    totalxp = models.IntegerField(default=0)
    categoryxp = models.JSONField(default=default_xp)
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

# Post model
class Post(models.Model):
    user = models.ForeignKey(
        Player, 
        on_delete=models.CASCADE, 
        related_name='posts'
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    post_image = CloudinaryField('image', blank=True, null=True)  # We'll handle public_id dynamically
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(check=~models.Q(title=''), name='title_not_empty'),
            models.CheckConstraint(check=~models.Q(content=''), name='content_not_empty')
        ]
        ordering = ['-created_at']  # Latest posts first

    def __str__(self):
        return f'{self.title} by {self.user.username}'

    def save(self, *args, **kwargs):
        # Only re-upload if a new image is added
        if self.pk is None and self.post_image:
            # Dynamically generate public_id based on user and post
            upload_result = cloudinary.uploader.upload(
                self.post_image,
                public_id=f"posts/user_{self.user.id}/{self.title}_{timezone.now().strftime('%Y%m%d%H%M%S')}",
                overwrite=True,
                resource_type="image"
            )
            self.post_image = upload_result['public_id']
        super().save(*args, **kwargs)