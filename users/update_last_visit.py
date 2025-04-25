
from django.utils.timezone import now
from django.utils.deprecation import MiddlewareMixin

class UpdateLastVisitMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            player = getattr(request.user, 'player', None)
            if player:
                player.last_visit = now()
                player.save(update_fields=['last_visit'])