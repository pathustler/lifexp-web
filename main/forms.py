from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'post_image', 'start_time', 'end_time', "tags"]
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'w-full  h-36 px-4 py-2 border rounded-lg focus:outline-none focus:ring focus:ring-blue-300 dark:bg-[#1f2022] dark:border-[#444] dark:text-white dark:focus:ring-blue-600 dark:placeholder-[#444]',
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
            'start_time': forms.TimeInput(attrs={  # Use TimeInput instead of FileInput
                'type': "time",
                'id': "start",
                'name': "start",
                'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring focus:ring-blue-300 dark:bg-[#1f2022] dark:border-[#444] dark:text-white dark:focus:ring-blue-600 dark:placeholder-[#444]',
            }),
            'end_time': forms.TimeInput(attrs={  # Use TimeInput instead of FileInput
                'type': "time",
                'id': "end",
                'name': "end",
                'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring focus:ring-blue-300 dark:bg-[#1f2022] dark:border-[#444] dark:text-white dark:focus:ring-blue-600 dark:placeholder-[#444]',
            }),
            'tags': forms.TextInput(attrs={
                'type': "hidden",
                'name': "tags",
                ':value': "tags.join(',')"
            }),
        }
