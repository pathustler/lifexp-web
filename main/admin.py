from django.contrib import admin
from .models import *
# Register your models here.


@admin.register(Post)
class Post(admin.ModelAdmin):
    list_display = ("content", "created_at")

@admin.register(ActivityLog)
class ActivityLog(admin.ModelAdmin):
    list_display = ("user","name", "xp_distribution", "created_at")
    
@admin.register(Comment)
class Comment(admin.ModelAdmin):
    list_display = ("post", "user", "content", "created_at")

