from django.shortcuts import get_object_or_404, render
from django.urls import path
from django.db.models import Q
from . import views
from rest_framework.decorators import api_view
from rest_framework.response import Response
from users.models import Player
import roman
from .forms import PostForm
from .models import Post, ActivityLog, Comment
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required




@login_required
def index(request):
    currentpage= "index"
    posts = Post.objects.select_related('user').all()
    activities = ActivityLog.objects.select_related('user').all()
    
    comments_map = {}
    for post in posts:
        top_comment = Comment.objects.filter(post=post, parent_comment=None).order_by('created_at').first()
        comments_map[post.id] = top_comment


    return render(request, 'main/index.html',{
        "currentpage": currentpage,
        'posts': posts, 
        'activities': activities,
        'comments_map': comments_map,
        'user': request.user
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
    query = request.GET.get('q', '')
    posts = Post.objects.filter(Q(tags__icontains=query) | Q(content__icontains=query)
)
    users = Player.objects.filter(username__icontains=query)
    
    context = {
        'posts': posts,
        'users': users,
        'recent_searches': ['Jason', 'Pat', 'ML project'],  # Fetch recent search from user model later
        'query': query,
    }
    return render(request, 'main/search.html', context)
   
from datetime import datetime


def new_post(request):
    currentpage= "new_post"
    user = Player.objects.get(username="danikavaughn")
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = PostForm(request.POST, request.FILES) 
        print(form)
        # check whether it's valid:
        if form.is_valid():
            # Create a new Post object
            start_time_obj = form.cleaned_data['start_time']
            end_time_obj = form.cleaned_data['end_time']

            print(start_time_obj)

            new_post = Post(
                user=user,  # Assign data from the form
                content=form.cleaned_data['content'],
                post_image=form.cleaned_data['post_image'],  # if this field exists
                start_time=start_time_obj,  # if this field exists
                end_time=end_time_obj,  # if this field exists
            )
            
            # Save the new post to the database
            new_post.save()

            # Redirect to the index view, not main/new_post
            return redirect('index')
            
            
            
            
        else:
            #print the error
            print(form.errors)
            return render(request, 'main/new_post.html', {
                "currentpage": currentpage,
                'form': form,
                'success': False
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

def add_comment(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)
        user = Player.objects.get(username=request.user.username)  # since you're using Player
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_comment_id')

        parent_comment = None
        if parent_id:
            parent_comment = Comment.objects.get(id=parent_id)

        Comment.objects.create(
            post=post,
            user=user,
            content=content,
            parent_comment=parent_comment
        )
        return redirect('post_detail', post_id=post_id)
