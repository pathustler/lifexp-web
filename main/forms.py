from django import forms 
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'post_image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring focus:ring-blue-300',
                'placeholder': 'Enter title...'
            }),
            'content': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring focus:ring-blue-300',
                'rows': 5,
                'placeholder': 'Write your post...'
            }),
            'post_image': forms.FileInput(attrs={
                'class': 'w-full cursor-pointer border border-gray-300 rounded-lg p-2 focus:outline-none'
            }),
        }