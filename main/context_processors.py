from .models import Post, ActivityLog, Comment
from .models import Comment, Post
from users.models import Player, UserSettings
import roman
from main.models import Activity

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
    
    dark_mode = dark_mode_context(request)
    
    activities_table = Activity.objects.all() if request.user.is_authenticated else None
    
    aspect_colors = {
        "physique": {
            "primary": "#8D2E2E",
            "secondary": "#EAAFAF",
            "icon": '''
            <svg class="h-3 w-3" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 512"><!--!Font Awesome Free 6.7.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc.--><path fill="#8d2e2e" d="M96 64c0-17.7 14.3-32 32-32l32 0c17.7 0 32 14.3 32 32l0 160 0 64 0 160c0 17.7-14.3 32-32 32l-32 0c-17.7 0-32-14.3-32-32l0-64-32 0c-17.7 0-32-14.3-32-32l0-64c-17.7 0-32-14.3-32-32s14.3-32 32-32l0-64c0-17.7 14.3-32 32-32l32 0 0-64zm448 0l0 64 32 0c17.7 0 32 14.3 32 32l0 64c17.7 0 32 14.3 32 32s-14.3 32-32 32l0 64c0 17.7-14.3 32-32 32l-32 0 0 64c0 17.7-14.3 32-32 32l-32 0c-17.7 0-32-14.3-32-32l0-160 0-64 0-160c0-17.7 14.3-32 32-32l32 0c17.7 0 32 14.3 32 32zM416 224l0 64-192 0 0-64 192 0z"/></svg>
            ''',
            "iconbig": '''
            <svg class="h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 512"><!--!Font Awesome Free 6.7.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc.--><path fill="#8d2e2e" d="M96 64c0-17.7 14.3-32 32-32l32 0c17.7 0 32 14.3 32 32l0 160 0 64 0 160c0 17.7-14.3 32-32 32l-32 0c-17.7 0-32-14.3-32-32l0-64-32 0c-17.7 0-32-14.3-32-32l0-64c-17.7 0-32-14.3-32-32s14.3-32 32-32l0-64c0-17.7 14.3-32 32-32l32 0 0-64zm448 0l0 64 32 0c17.7 0 32 14.3 32 32l0 64c17.7 0 32 14.3 32 32s-14.3 32-32 32l0 64c0 17.7-14.3 32-32 32l-32 0 0 64c0 17.7-14.3 32-32 32l-32 0c-17.7 0-32-14.3-32-32l0-160 0-64 0-160c0-17.7 14.3-32 32-32l32 0c17.7 0 32 14.3 32 32zM416 224l0 64-192 0 0-64 192 0z"/></svg>
            '''
        },
        "energy": {
            "primary": "#d0b400",
            "secondary": "#FDF099",
            "icon":'''
            <svg class="h-3 w-3" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><!--!Font Awesome Free 6.7.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc.--><path fill="#eccc00" d="M349.4 44.6c5.9-13.7 1.5-29.7-10.6-38.5s-28.6-8-39.9 1.8l-256 224c-10 8.8-13.6 22.9-8.9 35.3S50.7 288 64 288l111.5 0L98.6 467.4c-5.9 13.7-1.5 29.7 10.6 38.5s28.6 8 39.9-1.8l256-224c10-8.8 13.6-22.9 8.9-35.3s-16.6-20.7-30-20.7l-111.5 0L349.4 44.6z"/></svg>
            ''',
            "iconbig":'''
            <svg class="h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><!--!Font Awesome Free 6.7.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc.--><path fill="#eccc00" d="M349.4 44.6c5.9-13.7 1.5-29.7-10.6-38.5s-28.6-8-39.9 1.8l-256 224c-10 8.8-13.6 22.9-8.9 35.3S50.7 288 64 288l111.5 0L98.6 467.4c-5.9 13.7-1.5 29.7 10.6 38.5s28.6 8 39.9-1.8l256-224c10-8.8 13.6-22.9 8.9-35.3s-16.6-20.7-30-20.7l-111.5 0L349.4 44.6z"/></svg>
            '''
        },
        "social": {
            "primary": "#31784E",
            "secondary": "#AFEAC7",
            "icon":'''
                            <svg class="h-3 w-3" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><!--!Font Awesome Free 6.7.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc.--><path fill="#31784e" d="M96 128a128 128 0 1 0 256 0A128 128 0 1 0 96 128zm94.5 200.2l18.6 31L175.8 483.1l-36-146.9c-2-8.1-9.8-13.4-17.9-11.3C51.9 342.4 0 405.8 0 481.3c0 17 13.8 30.7 30.7 30.7l131.7 0c0 0 0 0 .1 0l5.5 0 112 0 5.5 0c0 0 0 0 .1 0l131.7 0c17 0 30.7-13.8 30.7-30.7c0-75.5-51.9-138.9-121.9-156.4c-8.1-2-15.9 3.3-17.9 11.3l-36 146.9L238.9 359.2l18.6-31c6.4-10.7-1.3-24.2-13.7-24.2L224 304l-19.7 0c-12.4 0-20.1 13.6-13.7 24.2z"/></svg>

    ''',
    "iconbig":'''
                            <svg class="h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><!--!Font Awesome Free 6.7.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc.--><path fill="#31784e" d="M96 128a128 128 0 1 0 256 0A128 128 0 1 0 96 128zm94.5 200.2l18.6 31L175.8 483.1l-36-146.9c-2-8.1-9.8-13.4-17.9-11.3C51.9 342.4 0 405.8 0 481.3c0 17 13.8 30.7 30.7 30.7l131.7 0c0 0 0 0 .1 0l5.5 0 112 0 5.5 0c0 0 0 0 .1 0l131.7 0c17 0 30.7-13.8 30.7-30.7c0-75.5-51.9-138.9-121.9-156.4c-8.1-2-15.9 3.3-17.9 11.3l-36 146.9L238.9 359.2l18.6-31c6.4-10.7-1.3-24.2-13.7-24.2L224 304l-19.7 0c-12.4 0-20.1 13.6-13.7 24.2z"/></svg>

    '''
        },
        "creativity": {
            "primary": "#4187A2",
            "secondary": "#AFD9EA",
            "icon": '''
                <svg class="h-3 w-3" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
                    <path fill="#4187a2" d="M184 0c30.9 0 56 25.1 56 56l0 400c0 30.9-25.1 56-56 56c-28.9 0-52.7-21.9-55.7-50.1c-5.2 1.4-10.7 2.1-16.3 2.1c-35.3 0-64-28.7-64-64c0-7.4 1.3-14.6 3.6-21.2C21.4 367.4 0 338.2 0 304c0-31.9 18.7-59.5 45.8-72.3C37.1 220.8 32 207 32 192c0-30.7 21.6-56.3 50.4-62.6C80.8 123.9 80 118 80 112c0-29.9 20.6-55.1 48.3-62.1C131.3 21.9 155.1 0 184 0zM328 0c28.9 0 52.6 21.9 55.7 49.9c27.8 7 48.3 32.1 48.3 62.1c0 6-.8 11.9-2.4 17.4c28.8 6.2 50.4 31.9 50.4 62.6c0 15-5.1 28.8-13.8 39.7C493.3 244.5 512 272.1 512 304c0 34.2-21.4 63.4-51.6 74.8c2.3 6.6 3.6 13.8 3.6 21.2c0 35.3-28.7 64-64 64c-5.6 0-11.1-.7-16.3-2.1c-3 28.2-26.8 50.1-55.7 50.1c-30.9 0-56-25.1-56-56l0-400c0-30.9 25.1-56 56-56z"/>
                </svg>
            ''',
            "iconbig": '''
                <svg class="h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
                    <path fill="#4187a2" d="M184 0c30.9 0 56 25.1 56 56l0 400c0 30.9-25.1 56-56 56c-28.9 0-52.7-21.9-55.7-50.1c-5.2 1.4-10.7 2.1-16.3 2.1c-35.3 0-64-28.7-64-64c0-7.4 1.3-14.6 3.6-21.2C21.4 367.4 0 338.2 0 304c0-31.9 18.7-59.5 45.8-72.3C37.1 220.8 32 207 32 192c0-30.7 21.6-56.3 50.4-62.6C80.8 123.9 80 118 80 112c0-29.9 20.6-55.1 48.3-62.1C131.3 21.9 155.1 0 184 0zM328 0c28.9 0 52.6 21.9 55.7 49.9c27.8 7 48.3 32.1 48.3 62.1c0 6-.8 11.9-2.4 17.4c28.8 6.2 50.4 31.9 50.4 62.6c0 15-5.1 28.8-13.8 39.7C493.3 244.5 512 272.1 512 304c0 34.2-21.4 63.4-51.6 74.8c2.3 6.6 3.6 13.8 3.6 21.2c0 35.3-28.7 64-64 64c-5.6 0-11.1-.7-16.3-2.1c-3 28.2-26.8 50.1-55.7 50.1c-30.9 0-56-25.1-56-56l0-400c0-30.9 25.1-56 56-56z"/>
                </svg>
            '''
        },
        "skill" : {
            "primary": "#713599",
            "secondary": "#BAAFEA",
            "icon":'''
            <svg
                   class="h-3 w-3" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"

                    xmlns="http://www.w3.org/2000/svg"
                    class="flex-grow-0 flex-shrink-0 w-2.5 h-2.5 relative"
                    preserveAspectRatio="xMidYMid meet"
                >
                <path d="M7.17944 4.63867C6.68982 4.73242 6.16894 4.56836 5.79043 4.14258L5.12892 3.39844C4.86848 3.10547 4.72263 2.71094 4.72263 2.29688V2.06055L3.33883 1.21094C3.24681 1.1543 3.18951 1.04297 3.19472 0.923828C3.19993 0.804688 3.26244 0.699219 3.35967 0.650391L4.17918 0.240234C4.49865 0.0820312 4.84417 0 5.1949 0H5.50916C6.14637 0 6.75927 0.273437 7.22285 0.763672L7.99722 1.58398C8.4174 2.0293 8.57366 2.67188 8.45907 3.26367L8.7334 3.57422L8.8723 3.41797C9.03551 3.23438 9.29942 3.23438 9.46089 3.41797L9.87759 3.88672C10.0408 4.07031 10.0408 4.36719 9.87759 4.54883L8.34968 6.26758C8.18647 6.45117 7.92256 6.45117 7.76109 6.26758L7.34439 5.79883C7.18118 5.61523 7.18118 5.31836 7.34439 5.13672L7.48329 4.98047L7.17944 4.63867ZM0.475736 7.36523L4.52991 3.56641C4.59068 3.66211 4.66013 3.75391 4.73479 3.83984L5.3963 4.58398C5.50048 4.70117 5.6116 4.80273 5.72966 4.89062L2.34222 9.46484C2.09046 9.80469 1.71716 10 1.32477 10C0.592065 10 0 9.33203 0 8.50977C0 8.06836 0.175362 7.64844 0.475736 7.36523Z" fill="#713599"></path>
            </svg>
            ''',
            "iconbig":'''
            <svg
                    class="h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"

                    xmlns="http://www.w3.org/2000/svg"
                    class="flex-grow-0 flex-shrink-0 w-2.5 h-2.5 relative"
                    preserveAspectRatio="xMidYMid meet"
                >
                <path d="M7.17944 4.63867C6.68982 4.73242 6.16894 4.56836 5.79043 4.14258L5.12892 3.39844C4.86848 3.10547 4.72263 2.71094 4.72263 2.29688V2.06055L3.33883 1.21094C3.24681 1.1543 3.18951 1.04297 3.19472 0.923828C3.19993 0.804688 3.26244 0.699219 3.35967 0.650391L4.17918 0.240234C4.49865 0.0820312 4.84417 0 5.1949 0H5.50916C6.14637 0 6.75927 0.273437 7.22285 0.763672L7.99722 1.58398C8.4174 2.0293 8.57366 2.67188 8.45907 3.26367L8.7334 3.57422L8.8723 3.41797C9.03551 3.23438 9.29942 3.23438 9.46089 3.41797L9.87759 3.88672C10.0408 4.07031 10.0408 4.36719 9.87759 4.54883L8.34968 6.26758C8.18647 6.45117 7.92256 6.45117 7.76109 6.26758L7.34439 5.79883C7.18118 5.61523 7.18118 5.31836 7.34439 5.13672L7.48329 4.98047L7.17944 4.63867ZM0.475736 7.36523L4.52991 3.56641C4.59068 3.66211 4.66013 3.75391 4.73479 3.83984L5.3963 4.58398C5.50048 4.70117 5.6116 4.80273 5.72966 4.89062L2.34222 9.46484C2.09046 9.80469 1.71716 10 1.32477 10C0.592065 10 0 9.33203 0 8.50977C0 8.06836 0.175362 7.64844 0.475736 7.36523Z" fill="#713599"></path>
            </svg>
            '''
        },
        
       
    }
    
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
        'dark_mode': dark_mode,  # Default: Light mode
        'aspect_colors' : aspect_colors,
        "activities_table":activities_table
    }

def dark_mode_context(request):
    dark_mode = True  # Default: Light mode

    if request.user.is_authenticated:
        try:
            user_settings = UserSettings.objects.get(player=request.user.player)
            dark_mode = (user_settings.appearance == "Dark")
        except UserSettings.DoesNotExist:
            pass  # Fallback to default

    return {"dark_mode": dark_mode}