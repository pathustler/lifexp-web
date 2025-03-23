from datetime import timezone
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
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    tags = models.TextField(blank=True, null=True)

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