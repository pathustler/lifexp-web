from rest_framework import serializers
from .models import Post, Comment

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'title', 'image', 'created_at','likes', 'user_liked']
        
    def get_user_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.player.id).exists()
        return False
    
    

class CommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    profile_picture = serializers.ImageField(source='user.profile_picture', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'post', 'user', 'username', 'profile_picture', 'content', 'created_at', 'parent_comment']
        read_only_fields = ['user', 'created_at']