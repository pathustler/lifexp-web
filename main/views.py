from django.shortcuts import get_object_or_404, render, redirect
from django.urls import path
from django.db.models import Q
from . import views
from rest_framework.decorators import api_view
from rest_framework.response import Response
from users.models import Player, UserSettings, Notification, SearchHistory
import roman
from .forms import PostForm
from .models import Post, ActivityLog, Comment, Like, Activity
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .serializers import CommentSerializer
import json
from collections import defaultdict
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils.timezone import now, timedelta
from django.db import models
from django.contrib import messages
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.urls import reverse


# venv\Scripts\activate my ref. ok


# recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
#     sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="sent_notifications")
#     notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
#     message = models.TextField(blank=True, null=True)
#     related_object_id = models.IntegerField(null=True, blank=True)  # ID of the related object (e.g., post, message)
#     created_at = models.DateTimeField(default=now)
#     is_read = models.BooleanField(default=False)

# Create an OpenAI client with your deepinfra token and endpoint



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
def get_comments(request):
    post_id = request.GET.get("post_id")
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post=post).order_by("-created_at")
    comment_list = [{
        "pfp": comment.user.profile_picture.url if comment.user.profile_picture else None,
        "username": comment.user.username,
        "fullname": comment.user.fullname,
        "text": comment.content
    } for comment in comments]
    return JsonResponse({"comments": comment_list})


import google.generativeai as genai


from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch




@require_POST
@login_required
def validate_post(request):
    try:
        # Get the uploaded image
        uploaded_file = request.FILES.get('image')
        if not uploaded_file:
            return JsonResponse({"status": "error", "message": "No image uploaded."}, status=400)

        # Open the image
        image = Image.open(uploaded_file).convert('RGB')

        # Load BLIP model and processor
        processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
        model = model.to("cpu")
        # Prepare inputs
        inputs = processor(image, return_tensors="pt")

        # Generate description
        with torch.no_grad():
            output = model.generate(**inputs)
        
        caption = processor.decode(output[0], skip_special_tokens=True)

        # Get the other form data
        content = request.POST.get('content', '')
        activities = request.POST.get('activities').split(',')  # activities sent as an array

        if not content or not activities:
            return JsonResponse({"status": "error", "message": "Missing content or activities."}, status=400)

        # Setup Gemini
        genai.configure(api_key="AIzaSyC5uY5Tlk8eVY42bL8ESvdxbj2vYBSGUik")
        g_model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17')

        # Create validation prompt
        prompt = f"""
You are a validation engine. The user is making a post about what they are doing (something productive). Your job is to verify if the image, content, and activities are logically related.

Image Description:
{caption}

Post Content:
{content}

Activities:
{', '.join(activities)}

Task:
- If the image, content, and activities are consistent and make sense together, respond exactly with: VALID
- If there are mismatches or unrelated elements (only if they are strictly unrelated, if they are related in some way, mark VALID), provide an error message with the format '<Error title in 2-10 words>|<Error Summary in 10-20 words>|<possible solution> in 10-20 words'.
- Error message example:
    Input: Picture : 'a road', Content: 'Just practiced by breaststroke in the pool, feeling very energetic', Activities: 'swimming, running'
    Ouput: 'That is not a pool...|You can't do breaststroke on a road, and that is definitely a road|Take a picture of the pool, or talk about running in the content'.
- Do not provide any other text or explanation.

Only reply with "VALID" or an error messages with the defined template.
"""

        # Send to Gemini
        response = g_model.generate_content(prompt)
        result = response.text.strip()

        # Return the validation result
        if result == "VALID":
            return JsonResponse({"status": "success", "message": "Post is valid"})
        else:
            return JsonResponse({"status": "error", "message": result})

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
from django.views.decorators.csrf import csrf_exempt

@login_required
def fetch_activity_info(request):

    try:
        activity_id = request.GET.get("activity_id") 
        activity = get_object_or_404(Activity, id=activity_id)
        

        activity_info = {
            'name': activity.name,
            'type': activity.activity_type,
            'created_at': activity.created_at.strftime('%d %B %Y'),
            'total_xp':activity.total_xp,
            'description': activity.description,
            'created_by': activity.created_by.username if activity.created_by and activity.created_by not in ['pat']  else "In built",
            
            'xp_distribution': activity.xp_distribution
        }
        return JsonResponse({"status": "success", "message": activity_info})
        
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

@login_required
def fetch_posts(request):
    player = Player.objects.get(username=request.user.username)
    page = int(request.GET.get('page', 1))  # Get the requested page number
    per_page = 5  # Number of posts to load per request

    # Get all posts
    all_posts = Post.objects.select_related('user', 'user__settings')

    # Get people you follow + yourself
    following_ids = player.following.values_list('id', flat=True)
    allowed_ids = list(following_ids) + [player.id]

    # Filter posts based on user privacy
    posts = all_posts.filter(
        Q(user__settings__account_type='Public') |
        Q(user__id__in=allowed_ids)
    )
    
    
    paginator = Paginator(posts, per_page)
    
    page_obj = paginator.get_page(page)
    post_list = []

    for post in page_obj:
        comments = Comment.objects.filter(post=post, parent_comment=None).order_by('created_at')[:3]  # Load top 3 comments
        comments_data = [{"id": c.id, "content": c.content, "user": c.user.fullname, "pfp":c.user.profile_picture.url} for c in comments]
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
            'logic': 0
        }
        xp_type_mapping = {
            "skill": "logic"  # skill was old, now treated as logic
        }
        for activity in post_activities:
            for xp_type, value in activity.xp_distribution.items():
                real_xp_type = xp_type_mapping.get(xp_type, xp_type)
                xp_data[real_xp_type] = xp_data.get(real_xp_type, 0) + value
            
        post_list.append({
            "id": post.id,
            "title": post.title,
            "content": post.content,  # Adjust fields as per your model
            "profile_picture": post.user.profile_picture.url if post.user.profile_picture else None,
            "fullname": post.user.fullname,
            "username": post.user.username,
            "created_at": post.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "post_image": post.post_image.url if post.post_image else None,
            "tags": post.tags if post.tags else None,  # Assuming tags are stored as a comma-separated string
            "user_id": post.user.id,
            "comments": comments_data,
            "likes":post.likes.count(),  
            "user_liked": post.likes.filter(liked_by=request.user.player).exists(),
            "xp_data": xp_data,
            "likedbyprofiles": likedbyprofiles,
            "own_post": request.user.player == post.user,
        })

    return JsonResponse({
        'posts': post_list,
        'has_next': page_obj.has_next()
    })

def mark_notifications_read(request):
    """Marks all unread notifications as read when user clicks."""
    
    if request.method == "POST":
        # Mark all unread notifications as read
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return JsonResponse({"status": "success"})  # Send success response
    
    return JsonResponse({"status": "error"}, status=400)


def clear_popup_flag(request):
    request.session['show_streak_popup'] = False
    return JsonResponse({'status': 'ok'})




@login_required
def index(request):
    currentpage = "index"
    player = Player.objects.get(username=request.user.username)
    # Get all posts
    all_posts = Post.objects.select_related('user', 'user__settings')

    # Get people you follow + yourself
    following_ids = player.following.values_list('id', flat=True)
    allowed_ids = list(following_ids) + [player.id]
    following_players = request.user.player.following.filter(streak_active=True).order_by('-streak_count')

    # Filter posts based on user privacy
    posts = all_posts.filter(
        Q(user__settings__account_type='Public') |
        Q(user__id__in=allowed_ids)
    )

    activities = ActivityLog.objects.select_related('user').all()
    rom = roman.toRoman(player.masterlevel)
    nextrom = roman.toRoman(player.masterlevel+1)
    title = f"{player.masterytitle} {rom}"
    userplayer = request.user.player
    
    # Exclude users already being followed + self
    following_ids = userplayer.following.values_list('id', flat=True)
    suggested_users = Player.objects.exclude(
        Q(id__in=following_ids) | Q(id=userplayer.id)
    )[:10]
    
    comments_map = {}
    for post in posts:
        top_comment = Comment.objects.filter(post=post, parent_comment=None).order_by('created_at').all()
        comments_map[post.id] = top_comment
       
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()
    notifications = notifications.filter(is_read=False)
    

   
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
        "suggested_users": suggested_users,
        'following_players': following_players,
    })
    
@login_required
def profile(request, username):
    currentpage = "profile"
    player = Player.objects.get(username=username)
    playerposts = Post.objects.filter(user=player)

    rom = roman.toRoman(player.masterlevel)
    title = f"{player.masterytitle} {rom}"
    
    is_following = request.user.player.following.filter(id=player.id).exists() if request.user.is_authenticated else False
    ownprofile = request.user.username == username

    today = now().date()
    start_date = today - timedelta(days=6)

    recent_activities = ActivityLog.objects.filter(user=player, created_at__date__gte=start_date)
    daily_xp_map = defaultdict(int)

    self_daily_xp_map = defaultdict(int)
    
    
    for activity in recent_activities:
        day = activity.created_at.strftime('%A')  # e.g., 'Monday'
        daily_xp_map[day] += sum(activity.xp_distribution.values())
        
    
        
    for activity in ActivityLog.objects.filter(user=request.user.player, created_at__date__gte=start_date):
        day = activity.created_at.strftime('%A')
        self_daily_xp_map[day] += sum(activity.xp_distribution.values())

    # Preserve order of weekdays
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    xp_data = [{"day": day, "xp": daily_xp_map.get(day, 0)} for day in weekdays]
    
    # Add self's xp data
    self_xp_data= [{"day": day, "xp": self_daily_xp_map.get(day, 0)} for day in weekdays]
    

    total_xp_week = sum(item["xp"] for item in xp_data)
    activities = ActivityLog.objects.filter(user=player)
    total_xp_all_time = 0

    for activity in activities:
        total_xp_all_time += sum(activity.xp_distribution.values())


    # Activity breakdown
    actlist = []
    for activity in activities:
        totalxp = sum(activity.xp_distribution.values())
        maxxplabel = max(activity.xp_distribution, key=activity.xp_distribution.get)
        maxxp = activity.xp_distribution[maxxplabel]

        for act in actlist:
            if act["name"] == activity.name:
                act["total_xp"] += totalxp
                for key in act["xp_distribution"]:
                    act["xp_distribution"][key] += activity.xp_distribution[key]
                
                actitem =Activity.objects.filter(name=activity.name)
                if actitem.exists():
                    act['max_xp_label'] = actitem[0].activity_type
                else:
                    act['max_xp_label'] = max(act["xp_distribution"], key=act["xp_distribution"].get)
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
    userprofile_secondary_color_rgba = hex_to_rgba(player.secondary_accent_color, 0.5)
    
    can_view_posts = (ownprofile or is_following or player.settings.account_type == "Public")
        
    
    return render(request, 'main/profile.html', {
        'player': player,
        "is_following": is_following,
        'username': username,
        'title': title,
        "xp_data": xp_data,
        "self_xp_data":self_xp_data,
        "total_xp_week": total_xp_week,
        "total_xp_all_time": total_xp_all_time,
        "currentpage": currentpage,
        "playerposts": playerposts,
        "actlist": actlist,
        "ownprofile": ownprofile,
        "userprofile_secondary_color_rgba": userprofile_secondary_color_rgba,
        'can_view_posts': can_view_posts,
        
    })

@login_required
def search(request):
    currentpage = "search"
    query = request.GET.get('q', '').strip()
    player = Player.objects.get(user=request.user)
    
    if query:
        # Filter posts by tags, content, or related activity name
        posts = Post.objects.filter(
            Q(tags__icontains=query) |
            Q(content__icontains=query) |
            Q(activity_logs__name__icontains=query)
        ).distinct()
        
        # Filter users by username or fullname
        users = Player.objects.filter(
            Q(username__icontains=query) |
            Q(fullname__icontains=query)
        )
        
        # Filter activities globally by name
        activities = ActivityLog.objects.filter(
            Q(name__icontains=query)
        ).select_related('user')
        
        # Store in history
        SearchHistory.objects.create(
            user=player,
            search_query=query,
            search_type='general',
        )
    else:
        # No query: show recent posts, some users, and user's recent activities
        posts = Post.objects.all().order_by('-created_at')[:12]  # Show 12 most recent posts
        users = Player.objects.all().order_by('?')[:6]  # Show 6 random users
        activities = ActivityLog.objects.filter(user=player).order_by('-created_at')[:10]
    
    recent_searches = SearchHistory.objects.filter(user=player).order_by('-searched_at')[:5]
    
    context = {
        'currentpage': currentpage,
        'query': query,
        'posts': posts,
        'users': users,
        'activities': activities,
        'recent_searches': recent_searches,
        'player': player
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
    
    activities_table = Activity.objects.all()
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = PostForm(request.POST, request.FILES) 
        print(form)
        # check whether it's valid:
        if form.is_valid():
            # Create a new Post object

            new_post = Post(
                user=player,  # Assign data from the form
                content=form.cleaned_data['content'],
                post_image=form.cleaned_data['post_image'],  # if this field exists
                tags=form.cleaned_data['tags'],  # if this field exists
            )
            # Save the new post to the database
            new_post.save()
            
            if request.POST.get("pre_liked") == "true":
                Like.objects.create(liked_by=player, post=new_post)
                
            print(form.cleaned_data['tags'])
            if form.cleaned_data['tags']:
            
             for tag in form.cleaned_data['tags'].split(','):
                xpdict = dict()
                if "logic" in tag:
                    xpdict["logic"] = random.randint(-20, 100)
                if "physique" in tag:
                    xpdict["physique"] = random.randint(-20, 100)
                if "creativity" in tag:
                    xpdict["creativity"] = random.randint(-20, 100)
                if "social" in tag:
                    xpdict["social"] = random.randint(-20, 100)
                if "energy" in tag:
                    xpdict["energy"] = random.randint(-20, 100)

                new_activity = ActivityLog(
                    post=new_post,
                    user=player,
                    name=tag,
                    xp_distribution={
                        "physique": random.randint(-5, 20) + xpdict.get("physique", 0),
                        "creativity": random.randint(-5, 20)+ xpdict.get("creativity", 0),
                        "social": random.randint(-5, 20)+   xpdict.get("social", 0),
                        "energy": random.randint(-5, 20)+   xpdict.get("energy", 0),
                        "logic": random.randint(-5, 20)+   xpdict.get("logic", 0)
                    }
                )
                
                player.update_streak()
                
                new_activity.save()
                
                
                
                
            # Redirect to the index view, not main/new_post
            return HttpResponseRedirect(reverse('index') + '?confetti=true')

            
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
        'player':player,

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
            "rookie":  ["A2A2A2","EAEAEA"],
        }
    
    label = type.capitalize()
    
    if request.user.player.masterytitle == "Rookie" and type == "rookie":
        rookie_users = Player.objects.filter(masterytitle="Rookie").order_by('totalxp').reverse()
        paginator = Paginator(rookie_users, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'main/rookieleaderboard.html',{
            "currentpage": currentpage,
            "type": type,
            "trophyurl": trophyurl,
            "primaryaccent": primseckey[type][0],
            "secondaryaccent": primseckey[type][1],
            "label": label,
            "rookie_users": rookie_users,
            "paginator": paginator,
            "page_obj": page_obj,
        })
    elif request.user.player.masterytitle == "Rookie" and type != "rookie":
        redirect("leaderboard", type="rookie")
    
    
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
    


@login_required
@csrf_exempt  # if using fetch, you may need this for testing; better to handle CSRF token properly
def create_custom_activity(request):
    if request.method == "POST":
        name = request.POST.get("name")

        
        act = Activity.objects.filter(name=name.capitalize())
        if act.exists():
            return JsonResponse({"status": "error", "message": "Activity already exists"}, status=400)


        genai.configure(api_key="AIzaSyC5uY5Tlk8eVY42bL8ESvdxbj2vYBSGUik")
        g_model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17')

        # Create validation prompt
        prompt = f"""
You are a validation engine for activity names.

Given an activity name, perform the following checks:

1. Check if it represents an actual, real-world activity (e.g., "Running", "Painting", "Programming").
2. Check if the activity would reasonably result in a positive score for at least one of the following aspects: physique, energy, social, creativity, or logic.
3. Check if it is a fundamental activity — it should not include explanations, durations (e.g., "for 2 hours"), combinations of multiple distinct actions (e.g., "running and cooking"), or overly detailed variations. It should be a basic, atomic action.

Respond according to the following rules:
- If all three checks pass, reply exactly with: VALID|<single activity type from Physique/Energy/Social/Creativity/Logic>|<a short 10-20 word fun fact about the activity>|<comma seperated list of xp distribution for each type when the activity is done without additional context for 1 hour, in the format Physique, Energy, Social, Creativity, Logic>.
  - Example: if the input is "Running", you could reply: VALID|Physique|The euphoric feeling after a run, known as "runner's high," is a real thing caused by the release of endorphins, which can help relieve stress and anxiety.|80,-20,0,-10,0
- If only checks 1 and 2 pass, but check 3 fails, reply with: WARNING|<one to three fundamentalized versions of the activity name separated by "|"> 
  - Example: if the input is "Running for 2 hours and lifting weights", you could reply: WARNING|Running|Weightlifting
- If either check 1 or check 2 fails, reply exactly with: INVALID

Only respond with VALID|...|..., WARNING|..., or INVALID — no additional explanations.

Activity to validate: "{name}"
"""

        # Send to Gemini
    
        response = g_model.generate_content(prompt)
        result = response.text.strip()
        print(result)
        
        
        if result.startswith("VALID|"):
            # Extract the activity type
            resultlist = result.split("|")

            print(resultlist)
            print(resultlist[1].lower())
            new_activity = Activity(
                name=name.capitalize(),
                activity_type=resultlist[1].lower(),
                description= resultlist[2],
                xp_distribution={
                    "physique": int(resultlist[3].split(",")[0]),
                    "energy": int(resultlist[3].split(",")[1]),
                    "social": int(resultlist[3].split(",")[2]),
                    "creativity": int(resultlist[3].split(",")[3]),
                    "logic": int(resultlist[3].split(",")[4])
                },
                created_by=request.user.player,  # Assuming you want to set the creator
            )
            new_activity.save()

            return JsonResponse({
                "status": "success",
                "name": new_activity.name,
                "activity_type": new_activity.activity_type
            })
            
        elif result.startswith("WARNING|"):
            # Extract the fundamentalized versions
            _, *fundamentalized_versions = result.split("|")
            return JsonResponse({
                "status": "warning",
                "message": "Activity name is too complex",
                "fundamentalized_versions": fundamentalized_versions
            })
        elif result == "INVALID":
            return JsonResponse({
                "status": "error",
                "message": "Activity name is invalid"
            })

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)
    


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
            if post.user != request.user.player:
                Notification.objects.create(
                    recipient=post.user.user,
                    sender=request.user,
                    notification_type='like',
                    message=f'liked your post',
                    related_object_id=post.id
                )

        return JsonResponse({"liked": liked, "like_count": post.likes.count()})

    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required
def history(request):

    activities = ActivityLog.objects.filter(user=request.user.player).select_related('post')
    print(activities)
    
    grouped_activities = defaultdict(list)

    for activity in activities:
        grouped_activities[activity.post].append(activity)

    return render(request, 'main/history.html', {
        'grouped_activities': grouped_activities.items(),  # List of (Post, [activities])
        'currentpage': 'profile'
    })

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # Make sure the current user owns the post
    if request.user != post.user.user:  # post.user is Player, post.user.user is actual User
        messages.error(request, "You don't have permission to delete this post.")
        return redirect('index')

    post.delete()
    messages.success(request, "Post deleted successfully.")
    return redirect('index')

@login_required
def report_post(request, post_id):
    pass

@login_required
def post_comment(request):
    if request.method == "POST":
        data = json.loads(request.body)
        post_id = data.get("post")
        content = data.get("content")

        post = get_object_or_404(Post, id=post_id)
        user = request.user.player

        comment = Comment.objects.create(post=post, user=user, content=content)

        return JsonResponse({
            "id": comment.id,
            "content": comment.content,
            "fullname": user.fullname,
            "profile_picture": user.profile_picture.url,
            "timestamp": "Just now"
        })

    return JsonResponse({"error": "Invalid request"}, status=400)

def notification_page(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    
    userplayer = request.user.player
    # Exclude users already being followed + self
    following_ids = userplayer.following.values_list('id', flat=True)
    suggested_users = Player.objects.exclude(
        Q(id__in=following_ids) | Q(id=userplayer.id)
    )[:10]
    
    
    return render(request, 'main/notifications.html', {
        'notifications': notifications,
        'currentpage': 'notifications',
        "suggested_users": suggested_users,
    })

@login_required
def delete_account(request):
    if request.method == "POST":
        user = request.user
        user.delete()
        messages.success(request, "Your account has been deleted successfully.")
        return redirect("index")  # or login page
    return redirect("settings")  # fallback

