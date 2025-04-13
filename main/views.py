from django.shortcuts import get_object_or_404, render, redirect
from django.urls import path
from django.db.models import Q
from . import views
from rest_framework.decorators import api_view
from rest_framework.response import Response
from users.models import Player, UserSettings, Notification, SearchHistory
import roman
from .forms import PostForm
from .models import Post, ActivityLog, Comment, Like
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from collections import defaultdict

# venv\Scripts\activate my ref. ok


# recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
#     sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="sent_notifications")
#     notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
#     message = models.TextField(blank=True, null=True)
#     related_object_id = models.IntegerField(null=True, blank=True)  # ID of the related object (e.g., post, message)
#     created_at = models.DateTimeField(default=now)
#     is_read = models.BooleanField(default=False)


def hex_to_rgba(hex_color, opacity=1):
    # Remove the hash (#) if it's present
    hex_color = hex_color.lstrip('#')

    # Handle shorthand hex notation (e.g., #abc -> #aabbcc)
    if len(hex_color) == 3:
        hex_color = ''.join([c * 2 for c in hex_color])

    # Extract the RGB components from the hex string
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    # Return the rgba value
    return f'rgba({r}, {g}, {b}, {opacity})'




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
        Notification.objects.create(
            recipient=player_to_follow.user,
            sender=request.user,
            notification_type='follow',
            message=f'started following you',
        )
        following = True

    return JsonResponse({"status": "success", "following": following})

@login_required
def fetch_posts(request):
    player = Player.objects.get(username=request.user.username)
    page = int(request.GET.get('page', 1))  # Get the requested page number
    per_page = 5  # Number of posts to load per request

    posts = Post.objects.select_related('user').order_by('-created_at')  # Adjust order as needed
    paginator = Paginator(posts, per_page)
    
    page_obj = paginator.get_page(page)
    post_list = []

    for post in page_obj:
        comments = Comment.objects.filter(post=post, parent_comment=None).order_by('created_at')[:3]  # Load top 3 comments
        comments_data = [{"id": c.id, "content": c.content, "user": c.user.username, "pfp":c.user.profile_picture.url} for c in comments]
        likedbyprofiles = []
        # i want 5 players followed by this  this user to be stored in the list, who have liked this post
        for like in post.likes.all():
            if like.liked_by in request.user.player.following.all():
                likedbyprofiles.append([like.liked_by.profile_picture.url, like.liked_by.username])
        # if the length of the list is greater than 5, remove the last element
        if len(likedbyprofiles) > 5:
            likedbyprofiles = likedbyprofiles[:5]

        
        
        post_activities = ActivityLog.objects.filter(post=post)
        xp_data = {
            'physique': 0,
            'creativity': 0,
            'social': 0,
            'energy': 0,
            'skill': 0
        }
        for activity in post_activities:
            for xp_type, value in activity.xp_distribution.items():
                xp_data[xp_type] += value
            
        post_list.append({
            "id": post.id,
            "content": post.content,  # Adjust fields as per your model
            "profile_picture": post.user.profile_picture.url if post.user.profile_picture else None,
            "fullname": post.user.fullname,
            "username": post.user.username,
            "created_at": post.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "post_image": post.post_image.url if post.post_image else None,
            "tags": post.tags if post.tags else None,  # Assuming tags are stored as a comma-separated string
            "start_time": post.start_time.strftime('%Y-%m-%d %H:%M:%S') if post.start_time else None,
            "end_time": post.end_time.strftime('%Y-%m-%d %H:%M:%S') if post.end_time else None,
            "user_id": post.user.id,
            "comments": comments_data,
            "likes":post.likes.count(),  
            "user_liked": post.likes.filter(liked_by=request.user.player).exists(),
            "xp_data": xp_data,
            "likedbyprofiles": likedbyprofiles,
        })

    return JsonResponse({
        'posts': post_list,
        'has_next': page_obj.has_next()
    })

def mark_notifications_read(request):
    """Marks all unread notifications as read when user hovers."""
    
    if request.method == "POST":
        # Mark all unread notifications as read
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return JsonResponse({"status": "success"})  # Send success response
    
    return JsonResponse({"status": "error"}, status=400)

@login_required
def index(request):
    currentpage = "index"
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
       
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()
   
    return render(request, 'main/index.html',{
        "currentpage": currentpage,
        'activities': activities,
        'comments_map': comments_map,
        'user': request.user,
        'title': title,
        'player': player,
        'nextrom': nextrom,
        "notifications": notifications,
        "unread_count": unread_count,
        # 'xp_data': xp_data,
        # 'xp_data_json': json.dumps(xp_data)
    })
@login_required
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
            

    userprofile_secondary_color_rgba = hex_to_rgba(player.secondary_accent_color, 0.5) 

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
        "actlist": actlist,
        "ownprofile": ownprofile,
        "userprofile_secondary_color_rgba": userprofile_secondary_color_rgba,
        })

@login_required
def search(request):
    currentpage= "search"
    query = request.GET.get('q', '')
    posts = Post.objects.filter(Q(tags__icontains=query) | Q(content__icontains=query))
    users = Player.objects.filter(username__icontains=query)
    player = Player.objects.get(user=request.user)
    
    if query:
        # Search for posts and users
        posts = Post.objects.filter(
            Q(content__icontains=query) | 
            Q(user__username__icontains=query)
        )
        users = Player.objects.filter(username__icontains=query)
        
        # Record search history if user is logged in
        if request.user.is_authenticated:
            SearchHistory.objects.create(
                user=player,
                search_query=query,
                search_type='general'
            )
    
    # Get recent searches for logged-in user
    recent_searches = SearchHistory.objects.filter(user=player).order_by('-searched_at')[:5]

    context = {
        'posts': posts,
        'users': users,
        'recent_searches': recent_searches,  # Fetch recent search from user model later
        'query': query,
        "currentpage": currentpage,
    }
    return render(request, 'main/search.html', context)

@login_required
@require_POST
def delete_search_history(request, id):
    player = Player.objects.get(user=request.user)
    try:
        search_history = SearchHistory.objects.get(id=id, user=player)
        search_history.delete()
        return JsonResponse({'status': 'success'})
    except SearchHistory.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Record not found'}, status=404)
    
import random
@login_required
def new_post(request):
    currentpage= "new_post"
    player = Player.objects.get(username=request.user.username)
    print(player.fullname)
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
            # Save the new post to the database
            new_post.save()
            
            if request.POST.get("pre_liked") == "true":
                Like.objects.create(liked_by=player, post=new_post)
            
            for tag in form.cleaned_data['tags'].split(','):
                xpdict = dict()
                if "skill" in tag:
                    xpdict["skill"] = random.randint(50, 100)
                if "physique" in tag:
                    xpdict["physique"] = random.randint(50, 100)
                if "creativity" in tag:
                    xpdict["creativity"] = random.randint(50, 100)
                if "social" in tag:
                    xpdict["social"] = random.randint(50, 100)
                if "energy" in tag:
                    xpdict["energy"] = random.randint(50, 100)

                new_activity = ActivityLog(
                    post=new_post,
                    user=player,
                    name=tag,
                    xp_distribution={
                        "physique": random.randint(0, 10) + xpdict.get("physique", 0),
                        "creativity": random.randint(0, 10)+ xpdict.get("creativity", 0),
                        "social": random.randint(0, 10)+   xpdict.get("social", 0),
                        "energy": random.randint(0, 10)+   xpdict.get("energy", 0),
                        "skill": random.randint(0, 10)+   xpdict.get("skill", 0)
                    }
                )
                
                new_activity.save()
                
            # Redirect to the index view, not main/new_post
            return redirect('index')
            
        else:
            #print the error
            print(form.errors)
            return render(request, 'main/new_post.html', {
                "currentpage": currentpage,
                'form': form,
                'success': False,
            })
            
    # if a GET (or any other method) we'll create a blank form
    else:
        form = PostForm()  # Also pass player here for the GET request
    
    return render(request, 'main/new_post.html',{
        "currentpage": currentpage,
        'form': form,
        'success': True,
        'player':player
    })
    
@login_required
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
    
@login_required    
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
@login_required
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
    player = request.user.player

    user_liked = post.likes.filter(liked_by=player).exists()
    
    comments_map = {}

    top_comment = Comment.objects.filter(post=post, parent_comment=None).order_by('created_at').all()
    comments_map[post.id] = top_comment
    
    return render(request, 'main/post_detail.html', {'post': post, 'comments_map': comments_map, 'user_liked': user_liked, 'player': player})



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


@login_required
def edit_profile(request):
    currentpage= "profile"
    player = Player.objects.get(username=request.user.username)
    
    if request.method == 'POST':
        player.fullname = request.POST.get('fullname')
        player.bio = request.POST.get('bio')
        player.title = request.POST.get('title')
        #Save the profile picture if it exists
        if request.FILES.get('profile_picture'):
            player.profile_picture = request.FILES.get('profile_picture')
        player.save()
        return redirect('profile', username=player.username)

    return render(request, 'main/edit_profile.html', {
        'player': player, 
        'currentpage': currentpage})
    
    
    
@csrf_exempt
@login_required
def like_post(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)
        player = request.user.player  # Assuming `Player` is linked to `User`

        if post.likes.filter(liked_by=player).exists():
            
            post.likes.filter(liked_by=player).delete()
            liked = False
        else:
            post.likes.create(liked_by=player)
            liked = True

        return JsonResponse({"liked": liked, "like_count": post.likes.count()})

    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required
def history(request):
    activities = ActivityLog.objects.filter(user=request.user.player).select_related('post')
    
    grouped_activities = defaultdict(list)

    for activity in activities:
        grouped_activities[activity.post].append(activity)

    return render(request, 'main/history.html', {
        'grouped_activities': grouped_activities.items(),  # List of (Post, [activities])
        'currentpage': 'history'
    })

