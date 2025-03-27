from django.shortcuts import get_object_or_404, render, redirect
from django.urls import path
from django.db.models import Q
from . import views
from rest_framework.decorators import api_view
from rest_framework.response import Response
from users.models import Player, UserSettings
import roman
from .forms import PostForm
from .models import Post, ActivityLog, Comment
from .models import Comment, Post
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

# wenv\Scripts\activate my ref. ok


@login_required
def toggle_follow(request, username):
    """Follow or unfollow a player"""
    player_to_follow = get_object_or_404(Player, username=username)
    user_player = request.user.player

    if user_player.is_following(player_to_follow):
        user_player.unfollow(player_to_follow)
        following = False
    else:
        user_player.follow(player_to_follow)
        following = True

    return JsonResponse({"status": "success", "following": following})
 

@login_required
def index(request):
    currentpage= "index"
    player = Player.objects.get(username=request.user.username)
    posts = Post.objects.select_related('user').all()
    activities = ActivityLog.objects.select_related('user').all()
    rom = roman.toRoman(player.masterlevel)
    nextrom = roman.toRoman(player.masterlevel+1)
    title = f"{player.masterytitle} {rom}"
    
    
    comments_map = {}
    for post in posts:
        top_comment = Comment.objects.filter(post=post, parent_comment=None).order_by('created_at').all()
        comments_map[post.id] = top_comment


    return render(request, 'main/index.html',{
        "currentpage": currentpage,
        'posts': posts, 
        'activities': activities,
        'comments_map': comments_map,
        'user': request.user,
        'title': title,
        'player': player,
        'nextrom': nextrom,

    })


def profile(request, username):
    currentpage= "profile"
    player = Player.objects.get(username=username)
    
    playerposts = Post.objects.filter(user=player)
    
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
    
    activities = ActivityLog.objects.filter(user=player)
    actlist = []
    
    is_following = request.user.player.following.filter(id=player.id).exists() if request.user.is_authenticated else False

    
    ownprofile = request.user.username == username
    

    for activity in activities:
        maxxp = activity.xp_distribution[max(activity.xp_distribution, key=activity.xp_distribution.get)]
        maxxplabel = max(activity.xp_distribution, key=activity.xp_distribution.get)
        totalxp = sum(activity.xp_distribution.values())
        #if the activity of that name already exists in actlist, add total xp to it and update the max xp label
        for act in actlist:
            if act["name"] == activity.name:
                act["total_xp"] += totalxp
                
                    
                #add both's xp_distribution
                for key in act["xp_distribution"]:
                    act["xp_distribution"][key] += activity.xp_distribution[key]
                act['max_xp_label'] = max(act["xp_distribution"], key=act["xp_distribution"].get)
                
                print(act)
                
                break
        else:
            actlist.append({
                "name": activity.name,
                "total_xp": totalxp,
                "max_xp_label": maxxplabel,
                "max_xp": maxxp,
                "xp_distribution": activity.xp_distribution
            })
            

        

    actlist.sort(key=lambda x: x["total_xp"], reverse=True)
    
    total_xp_week = sum(item["xp"] for item in xp_data)
    total_xp_all_time = 2312320  # Replace with actual database value
    
    return render(request, 'main/profile.html', {
        'player': player,
        "is_following": is_following,
        'username': username,
        'title': title,
         "xp_data": xp_data,
        "total_xp_week": total_xp_week,
        "total_xp_all_time": total_xp_all_time,
        "currentpage": currentpage,
        "playerposts": playerposts,
        "dark_mode": False,
        "actlist": actlist,
        "ownprofile": ownprofile
        })

def search(request):
    currentpage= "search"
    query = request.GET.get('q', '')
    posts = Post.objects.filter(Q(tags__icontains=query) | Q(content__icontains=query)
)
    users = Player.objects.filter(username__icontains=query)
    
    context = {
        'posts': posts,
        'users': users,
        'recent_searches': ['Jason', 'Pat', 'ML project'],  # Fetch recent search from user model later
        'query': query,
        "currentpage": currentpage,
    }
    return render(request, 'main/search.html', context)



def new_post(request):
    currentpage= "new_post"
    player = Player.objects.get(username=request.user.username)
    print(player.fullname)
    
    # user = request.user.player

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
                user=player,  # Assign data from the form
                content=form.cleaned_data['content'],
                post_image=form.cleaned_data['post_image'],  # if this field exists
                start_time=start_time_obj,  # if this field exists
                end_time=end_time_obj,  # if this field exists
                tags=form.cleaned_data['tags'],  # if this field exists
            )
            
            for tag in form.cleaned_data['tags'].split(','):

                new_activity = ActivityLog(
                    user=player,
                    name=tag,
                    start_time=start_time_obj,
                    end_time=end_time_obj,
                )
                
                new_activity.save()
                
            
            
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
                'success': False,
                'player':player
            })
            
    # if a GET (or any other method) we'll create a blank form
    else:
        form = PostForm()
        
    return render(request, 'main/new_post.html',{
        "currentpage": currentpage,
        'form': form,
        'success': True,
        'player':player
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
    player = Player.objects.get(username=request.user.username)
    settings, created = UserSettings.objects.get_or_create(player=player)

    if request.method == 'POST':
        settings.account_type = request.POST.get('account_type', 'Public')
        settings.notifications = request.POST.get('notifications', 'On')
        settings.appearance = request.POST.get('appearance', 'Light')
        settings.save()
        return redirect('settings')

    return render(request, 'main/settings.html', {'settings': settings, 'currentpage': currentpage, 'player': player})

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
    


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    comments_map = {}

    top_comment = Comment.objects.filter(post=post, parent_comment=None).order_by('created_at').all()
    comments_map[post.id] = top_comment

    return render(request, 'main/post_detail.html', {'post': post, 'comments_map': comments_map,})



@login_required
def add_comment(request, post_id):
    if request.method == "POST":
        post = Post.objects.get(id=post_id)
        user = request.user
        content = request.POST['content']
        Comment.objects.create(post=post, user=user, content=content)
    return redirect('index')

@login_required
def add_reply(request, comment_id):
    if request.method == "POST":
        parent_comment = Comment.objects.get(id=comment_id)
        post = parent_comment.post
        user = request.user
        content = request.POST['content']
        Comment.objects.create(post=post, user=user, content=content, parent_comment=parent_comment)
    return redirect('index')