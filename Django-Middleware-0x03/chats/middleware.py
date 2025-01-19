from datetime import datetime
from typing import Callable
import logging

# Configure logging
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
