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
import google.generativeai as genai


def clean_summary(text):
    # Find last period, exclamation, or question mark
    for end in [".", "!", "?"]:
        if end in text:
            return text[:text.rfind(end)+1]
    return text  # fallback if no punctuation found

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
    duration = models.DurationField(null=True, blank=True)
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
        if not self.title:
            genai.configure(api_key="AIzaSyC5uY5Tlk8eVY42bL8ESvdxbj2vYBSGUik")
            # Load the Gemini model
            model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17')
            prompt = f"This is the content of a post by a user who shows something productive they did. Give exactly one suitable title of around 1-6 words, do not output anything other than the title:\n\n{self.content}"
            response = model.generate_content(prompt)
            self.title = response.text.strip()
        
        
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
            "logic": 0
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
    
    def default_xp():
        return {
            "physique": 0,
            "creativity": 0,
            "social": 0,
            "energy": 0,
            "logic": 0
        }
    
    
    name = models.CharField(max_length=255)
    activity_type = models.CharField(max_length=255, choices=[
        ('physique', 'Physique'),
        ('creativity', 'Creativity'),
        ('social', 'Social'),
        ('energy', 'Energy'),
        ('logic', 'Logic')
    ])
    
    used_posts = models.ManyToManyField(Post, blank=True, related_name='activities')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(Player,null=True, blank=True, on_delete=models.CASCADE, related_name='activities')
    total_xp = models.IntegerField(blank=True, null=True)
    xp_distribution = models.JSONField(default=default_xp)
    
    
    
    def save(self, *args, **kwargs):
    # First time saving (new object)
        if not self.pk or not self.total_xp:
            self.total_xp = sum(self.xp_distribution.values())
        else:
            try:
                old = self.__class__.objects.get(pk=self.pk)
                if old.xp_distribution != self.xp_distribution:
                    self.total_xp = sum(self.xp_distribution.values())
            except self.__class__.DoesNotExist:
                # In case somehow the pk is set but object not found
                self.total_xp = sum(self.xp_distribution.values())

        super().save(*args, **kwargs)