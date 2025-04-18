from django import forms
from .models import Post
from users.models import Player

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'post_image', "tags"]
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'w-full  h-36 px-4 py-2 border rounded-lg focus:outline-none dark:bg-[#1f2022] dark:border-[#444] dark:text-white dark:placeholder-[#444] dynamic-focus',
                'rows': 5,
                'placeholder': 'Describe your post...'
            }),
            'post_image': forms.FileInput(attrs={
                'id': 'image',
                'name': 'image',
                'accept': 'image/*',
                'class': 'absolute inset-0 opacity-0 cursor-pointer placeholder-[#444]',
                'onchange': 'previewImage(event)',
            }),
            
            'tags': forms.TextInput(attrs={
                'type': "hidden",
                'name': "tags",
                ':value': "tags.join(',')"
            }),
        }
