from django import forms 
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'post_image', 'start_time', 'end_time']
        widgets = {
           
            'content': forms.Textarea(attrs={
                'class': 'w-full  h-36 px-4 py-2 border rounded-lg focus:outline-none focus:ring focus:ring-blue-300',
                'rows': 5,
                'placeholder': 'Descibe your post...'
            }),
            'post_image': forms.FileInput(attrs={
                'class': 'w-full cursor-pointer border border-gray-300 rounded-lg p-2 focus:outline-none'
            }),
            'start_time': forms.FileInput(attrs={
                'type':"time",
                'id':"start",
                'name':"start",
                'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring focus:ring-blue-300',
            }),
            'end_time': forms.FileInput(attrs={
                'type':"time",
                'id':"end",
                'name':"end",
                'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring focus:ring-blue-300',
            })
        
        }