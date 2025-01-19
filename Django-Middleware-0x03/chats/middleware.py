import logging
from datetime import datetime, timedelta
from typing import Callable
from django.http import HttpResponseForbidden

logging.basicConfig(
    filename='requests.log',
    level=logging.INFO,
    format='%(message)s'
)


class RequestLoggingMiddleware:
    """
    Existing logging middleware
    """
    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user.username if request.user.is_authenticated else 'Anonymous'
        logging.info(f"{datetime.now()} - User: {user} - Path: {request.path}")

        return self.get_response(request)


class RestrictAccessByTimeMiddleware:
    """
    Existing time-based access restriction middleware
    """
    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request):
        current_hour = datetime.now().hour
        # Allow only 9 AM to 6 PM (adjust as needed)
        if current_hour < 9 or current_hour >= 18:
            return HttpResponseForbidden("Access to the chat is restricted outside of 9 AM to 6 PM.")

        return self.get_response(request)


class OffensiveLanguageMiddleware:
    """
    Middleware that enforces a rate limit on chat message creation, 
    based on a client's IP address. (E.g. max 5 messages per 1 minute.)

    Despite the name, this example focuses on limiting the number of 
    messages in a timeframe. For actual 'offensive language' filtering, 
    you'd parse the message content and block it if it contains 
    restricted terms.
    """

    # Allowed messages in time window
    MAX_MESSAGES = 5
    # Time window in seconds (e.g., 60 = 1 minute)
    TIME_WINDOW = 60

    def __init__(self, get_response: Callable):
        self.get_response = get_response

        # Tracks IP -> list of recent POST (message) timestamps
        self.ip_tracking = {}

    def __call__(self, request):
        # We only want to rate-limit requests that create/send messages.
        # For simplicity, let's check if it's a POST to any "/messages" endpoint.
        # Adjust as necessary for your use-case (e.g., /api/messages).
        if request.method == 'POST' and '/messages' in request.path.lower():
            ip_address = self._get_client_ip(request)
            now = datetime.now()

            # Initialize tracking for this IP if not present
            if ip_address not in self.ip_tracking:
                self.ip_tracking[ip_address] = []

            # Filter out timestamps older than TIME_WINDOW from now
            window_start = now - timedelta(seconds=self.TIME_WINDOW)
            recent_timestamps = [
                t for t in self.ip_tracking[ip_address] if t > window_start
            ]

            # Check how many requests remain in the window after cleaning
            if len(recent_timestamps) >= self.MAX_MESSAGES:
                # Block the request
                return HttpResponseForbidden(
                    "Message limit exceeded. Please wait before sending more messages."
                )

            # Otherwise, record the current request's timestamp
            recent_timestamps.append(now)
            self.ip_tracking[ip_address] = recent_timestamps

        # Proceed with the request if not blocked
        return self.get_response(request)

    def _get_client_ip(self, request):
        """
        Helper method to safely extract the IP address 
        from the request headers (including proxies).
        """
        # If behind a proxy/load balancer, the real IP could be in HTTP_X_FORWARDED_FOR
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # x_forwarded_for may contain multiple IPs, first is the client’s
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', None)
        return ip or "unknown"

class RolepermissionMiddleware:
    """
    Middleware that ensures only users with certain roles 
    (e.g. admin or moderator) can proceed for protected actions.
    If user is not authenticated or does not have one of these roles, 
    return a 403 Forbidden.
    """

    ALLOWED_ROLES = ['admin', 'moderator']  # or use ['admin', 'host'] if 'host' acts like 'moderator'

    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user

        # Only check role if the user is authenticated
        if user.is_authenticated:
            # If the user's role is not in ALLOWED_ROLES, block the request
            if getattr(user, 'role', None) not in self.ALLOWED_ROLES:
                return HttpResponseForbidden(
                    "You do not have permission to perform this action."
                )
        else:
            # If not authenticated, also forbid
            return HttpResponseForbidden(
                "You must be logged in with sufficient privileges."
            )

        return self.get_response(request)