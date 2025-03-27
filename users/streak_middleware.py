from datetime import timedelta
from django.utils.timezone import now
from main.models import Player

class StreakMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            player, created = Player.objects.get_or_create(user=request.user)
            player.update_streak()
            
        return self.get_response(request)
