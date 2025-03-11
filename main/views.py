from django.shortcuts import render
from django.urls import path
from . import views

# Create your views here.
def index(request):
    return render(request, 'main/index.html')


def profile(request, username):
    
    return render(request, 'main/profile.html', {'username': username})
