from django.utils import timezone
from django.db import models
from LifeXP import settings
from cloudinary.models import CloudinaryField
import cloudinary
import cloudinary.uploader
import cloudinary.api
from users.models import Player
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

cloudinary.config( 
  cloud_name = settings.CLOUDINARY_STORAGE['CLOUD_NAME'], 
  api_key = settings.CLOUDINARY_STORAGE['API_KEY'], 
  api_secret = settings.CLOUDINARY_STORAGE['API_SECRET'],
  secure = True 
)

# Create your models here.
# from openai import OpenAI
# def generateHeading(postContent):
#     openai = OpenAI(
#         api_key="$DEEPINFRA_TOKEN",
#         base_url="https://api.deepinfra.com/v1/openai",
#     )

#     chat_completion = openai.chat.completions.create(
#         model="Qwen/QwQ-32B",
#         messages=[{"role": "user", "content": f"Generate Heading for this post: {postContent}"}],
#     )

#     print(chat_completion.choices[0].message.content)
#     print(chat_completion.usage.prompt_tokens, chat_completion.usage.completion_tokens)
#     return chat_completion.choices[0].message.content


# Post model
class Post(models.Model):
    user = models.ForeignKey(
        Player, 
        on_delete=models.CASCADE, 
        related_name='posts'
    )
    title = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField()
    post_image = CloudinaryField('image', blank=True, null=True)  # We'll handle public_id dynamically
    
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
        # if not self.title:
        #     self.title = generateHeading(self.content)
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
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='activity_logs')
    name = models.CharField(max_length=255, blank=True, null=True)
    xp_distribution = models.JSONField(default=default_xp)
    
    # We'll auto-calculate this in minutes
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
    
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

@receiver(post_save, sender=ActivityLog)
@receiver(post_delete, sender=ActivityLog)
def update_user_xp(sender, instance, **kwargs):
    instance.user.update_category_xp()
    
    
class Like(models.Model):
    liked_by = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="likes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    liked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('liked_by', 'post')  # Prevents duplicate likes

    def __str__(self):
        return f"{self.liked_by.fullname} liked {self.post.content[:5]}"
    
    
    
class Activity(models.Model):
    
    
    
    
    name = models.CharField(max_length=255)
    activity_type = models.CharField(max_length=255, choices=[
        ('physique', 'Physique'),
        ('creativity', 'Creativity'),
        ('social', 'Social'),
        ('energy', 'Energy'),
        ('skill', 'Skill')
    ])
    
    