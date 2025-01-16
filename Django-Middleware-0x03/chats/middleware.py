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
        # Get user info (authenticated or anonymous)
        user = request.user.username if request.user.is_authenticated else 'Anonymous'
        
        # Log the request
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        logging.info(log_message)
        
        # Process the request
        response = self.get_response(request)
        
        return response 