from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin


class UpdateLastSeenMiddleware(MiddlewareMixin):
 

    def process_request(self, request):
        if request.user.is_authenticated:
            request.user.last_seen = timezone.now()
            request.user.save(update_fields=["last_seen"])