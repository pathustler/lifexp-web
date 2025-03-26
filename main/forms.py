from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'post_image', 'start_time', 'end_time', "tags"]
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'w-full  h-36 px-4 py-2 border rounded-lg focus:outline-none focus:ring focus:ring-blue-300',
                'rows': 5,
                'placeholder': 'Describe your post...'
            }),
            'post_image': forms.FileInput(attrs={
                'id': 'image',
                'name': 'image',
                'accept': 'image/*',
                'class': 'absolute inset-0 opacity-0 cursor-pointer',
                'onchange': 'previewImage(event)',
            }),
            'start_time': forms.DateTimeInput(attrs={  # Use TimeInput instead of FileInput
                'type': "datetime-local",
                'id': "start",
                'name': "start",
                'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring focus:ring-blue-300',
            }),
            'end_time': forms.DateTimeInput(attrs={  # Use TimeInput instead of FileInput
                'type': "datetime-local",
                'id': "end",
                'name': "end",
                'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring focus:ring-blue-300',
            }),
            'tags': forms.TextInput(attrs={
                'type': "hidden",
                'name': "tags",
                ':value': "tags.join(',')"
            }),
        }
