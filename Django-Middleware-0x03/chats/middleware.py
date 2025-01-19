import logging
from datetime import datetime
from typing import Callable
from django.http import HttpResponseForbidden

# Configure logging for RequestLoggingMiddleware (existing)
logging.basicConfig(
    filename='requests.log',
    level=logging.INFO,
    format='%(message)s'
)

class RequestLoggingMiddleware:
    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request):
        # Determine if a user is authenticated; otherwise, label as "Anonymous"
        user = request.user.username if request.user.is_authenticated else 'Anonymous'

        # Format the log message
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"

        # Write log entry to requests.log
        logging.info(log_message)

        # Call the next middleware or view
        response = self.get_response(request)
        return response


class RestrictAccessByTimeMiddleware:
    """
    Middleware that denies access outside of the allowed time window 
    (e.g., 9:00 AM to 6:00 PM).
    """

    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request):
        current_time = datetime.now().time()
        current_hour = current_time.hour

        # Deny access if it is before 9 AM or after/equal 6 PM
        if current_hour < 9 or current_hour >= 18:
            return HttpResponseForbidden(
                "Access to the chat is restricted outside of 9 AM to 6 PM."
            )

        return self.get_response(request)
