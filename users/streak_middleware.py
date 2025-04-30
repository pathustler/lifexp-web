from datetime import timedelta
from django.utils.timezone import now
from main.models import Post, Player

class UpdateStreakMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                player = Player.objects.get(username=request.user.username)
                today = now().date()
                latest_post = Post.objects.filter(user=player).order_by('-created_at').first()
                request.session['show_streak_popup'] = False
                if not latest_post:
                    # If no posts exist, set streak_active to False
                    player.streak_active = False
                    player.streak_count = 0
                    player.save()
                    return self.get_response(request)
                # Reset streak_active if it's a new day
                if latest_post and latest_post.created_at.date() != today:
                    player.streak_active = False
                    player.save()
                #set streak as 0 if last post was more than 2 days ago
                if latest_post and latest_post.created_at.date() < (today - timedelta(days=2)):
                    player.streak_count = 0
                    player.streak_active = False
                    player.save()
                    
                # if a post was made today, set streak_active to true
                if not player.streak_active and latest_post and latest_post.created_at.date() == today:
                    player.streak_active = True
                    player.streak_count += 1
                    player.save()
                    request.session['show_streak_popup'] = True
                    
                
                
                    
                
            except Player.DoesNotExist:
                pass

        return self.get_response(request)
