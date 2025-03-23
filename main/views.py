from django.shortcuts import render
from django.urls import path
from . import views
from users.models import Player
import roman
from .forms import PostForm
from .models import Post, ActivityLog

def index(request):
    currentpage= "index"
    posts = Post.objects.select_related('user').all()
    activities = ActivityLog.objects.select_related('user').all()
    return render(request, 'main/index.html',{
        "currentpage": currentpage,
        'posts': posts, 
        'activities': activities
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
    
def new_post(request):
    currentpage= "new_post"
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = PostForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            form.save()
            return render(request, 'main/new_post.html',{
                "currentpage": currentpage,
                'form': form,
                'success': True
            })
    # if a GET (or any other method) we'll create a blank form
    else:
        form = PostForm()
        
    return render(request, 'main/new_post.html',{
        "currentpage": currentpage,
        'form': form,
        'success': False
    })
    
    
def leaderboard(request, type):
    currentpage= "leaderboard"
    trophyurl = "images/leaderboard/"+type+".png"
    primseckey = {
            "warrior":  ["8D2E2E","EAAFAF"],
            "protagonist":  ["ECCC00","FDF099"],
            "diplomat":  ["31784E","AFEAC7"],
            "maverick":  ["4187A2","AFD9EA"],
            "prodigy":  ["713599","BAAFEA"],
        }
    
    label = type.capitalize()
    
    
    
    
    
    return render(request, 'main/leaderboard.html',{
        "currentpage": currentpage,
        "type": type,
        "trophyurl": trophyurl,
        "primaryaccent": primseckey[type][0],
        "secondaryaccent": primseckey[type][1],
        "label": label
    })
    
    
def settings(request):
    currentpage= "settings"
    return render(request, 'main/settings.html',{
        "currentpage": currentpage
    })