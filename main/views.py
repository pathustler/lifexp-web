from django.shortcuts import render
from django.urls import path
from . import views
from users.models import Player
import roman

# Create your views here.
def index(request):
    return render(request, 'main/index.html')


def profile(request, username):
    player = Player.objects.get(username=username)
    
    rom = roman.toRoman(player.masterlevel)
    title = f"{player.masterytitle} {rom}"
    
    titlemaster={
        "Warrior": 0,
        "Protagonist": 1,
        "Diplomat": 2,
        "Maverick": 3,
        "Prodigy": 4
    }
    if player.masterytitle == "Rookie":
        pass
    
    
    
    return render(request, 'main/profile.html', {
        'player': player,
        'username': username,
        'title': title,
        })
