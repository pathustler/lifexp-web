from django.shortcuts import render
from django.urls import path
from . import views
from users.models import Player
import roman

# Create your views here.
def index(request):
    currentpage= "index"
    return render(request, 'main/index.html',{
        "currentpage": currentpage
    })


def profile(request, username):
    currentpage= "profile"
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
    
    
    
    xp_data = [
        {"day": "Monday", "xp": 200},
        {"day": "Tuesday", "xp": 20},
        {"day": "Wednesday", "xp": 90},
        {"day": "Thursday", "xp": 130},
        {"day": "Friday", "xp": 5},
        {"day": "Saturday", "xp": 2},
    ]
    
    total_xp_week = sum(item["xp"] for item in xp_data)
    total_xp_all_time = 2312320  # Replace with actual database value
    
    
    
    return render(request, 'main/profile.html', {
        'player': player,
        'username': username,
        'title': title,
         "xp_data": xp_data,
        "total_xp_week": total_xp_week,
        "total_xp_all_time": total_xp_all_time,
        "currentpage": currentpage
        })


def search(request):
    currentpage= "search"
    return render(request, 'main/search.html',{
        "currentpage": currentpage
    })