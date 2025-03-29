from .models import Post, ActivityLog, Comment
from .models import Comment, Post
from users.models import Player
import roman


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


def global_variables(request):
    player = Player.objects.get(username=request.user.username) if request.user.is_authenticated else None
    posts = Post.objects.select_related('user').all() if request.user.is_authenticated else None
    activities = ActivityLog.objects.select_related('user').all() if request.user.is_authenticated else None
    
    if request.user.is_authenticated and player: 
        rom = roman.toRoman(player.masterlevel)
    else:
        rom = None
        
    nextrom = roman.toRoman(player.masterlevel+1) if request.user.is_authenticated and player else None
    title = f"{player.masterytitle} {rom}" if request.user.is_authenticated and player else None
    
    secondary_color_rgba = hex_to_rgba(player.secondary_accent_color, 0.5) if request.user.is_authenticated and player else None
    
    return {
        'default_profile_picture': "https://res.cloudinary.com/dfohn9dcz/image/upload/v1742902918/default_profile.png",
        'site_name': "LifeXP",
        'user': request.user ,
        'is_authenticated': request.user.is_authenticated,
        'player': request.user.player if request.user.is_authenticated else None,
        "userplayer": request.user.player if request.user.is_authenticated else None,
        'mastery':request.user.player.masterytitle.lower() if request.user.is_authenticated else None,
        'posts': posts, 
        'activities': activities,
        'title': title,
        'nextrom': nextrom,
        'secondary_color_rgba': secondary_color_rgba,
        "dark_mode": True,
    }
