from django.utils import timezone
from django.db import models
from LifeXP import settings
from cloudinary.models import CloudinaryField
import cloudinary
import cloudinary.uploader
import cloudinary.api
from users.models import Player

cloudinary.config( 
  cloud_name = settings.CLOUDINARY_STORAGE['CLOUD_NAME'], 
  api_key = settings.CLOUDINARY_STORAGE['API_KEY'], 
  api_secret = settings.CLOUDINARY_STORAGE['API_SECRET'],
  secure = True 
)

# Create your models here.

# Post model
class Post(models.Model):
    user = models.ForeignKey(
        Player, 
        on_delete=models.CASCADE, 
        related_name='posts'
    )
    content = models.TextField()
    post_image = CloudinaryField('image', blank=True, null=True)  # We'll handle public_id dynamically
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    tags = models.CharField(max_length=255, blank=True, null=True) 

    class Meta:
        constraints = [
            models.CheckConstraint(check=~models.Q(content=''), name='content_not_empty')
        ]
        ordering = ['-created_at']  # Latest posts first

    def __str__(self):
        return f'{self.content[:15]} by {self.user.username}'

    def save(self, *args, **kwargs):
        # Only re-upload if a new image is added
        if self.pk is None and self.post_image:
            # Dynamically generate public_id based on user and post
            upload_result = cloudinary.uploader.upload(
                self.post_image,
                public_id=f"posts/user_{self.user.id}/{self.content[:3]}_{timezone.now().strftime('%Y%m%d%H%M%S')}",
                overwrite=True,
                resource_type="image"
            )
            self.post_image = upload_result['public_id']
        
        super().save(*args, **kwargs)

# ActivityLog model
class ActivityLog(models.Model):
    def default_xp():
        return {
            "physique": 0,
            "creativity": 0,
            "social": 0,
            "energy": 0,
            "skill": 0
        }
    user = models.ForeignKey(
        Player, 
        on_delete=models.CASCADE, 
        related_name='activity_logs'
    )
    name = models.CharField(max_length=255, blank=True, null=True)
    xp_distribution = models.JSONField(default=default_xp)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
    # We'll auto-calculate this in minutes
    total_time_done = models.IntegerField(editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # Calculate the total time duration in minutes before saving
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            self.total_time_done = int(duration.total_seconds() / 60)  # or /60 for minutes, /3600 for hours
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Activity by {self.user.username} on {self.created_at.strftime("%Y-%m-%d")}'

class Comment(models.Model):
    post = models.ForeignKey(
        Post, 
        on_delete=models.CASCADE, 
        related_name='comments'
    )
    user = models.ForeignKey(
        Player, 
        on_delete=models.CASCADE, 
        related_name='comments'
    )
    parent_comment = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='replies'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.user.username} on {self.post.id}'
