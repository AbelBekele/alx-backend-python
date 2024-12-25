# chats/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet

# Initialize the default router
router = DefaultRouter()

# Register viewsets with the router
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')

# Define URL patterns
urlpatterns = [
    # Include the router URLs
    path('', include(router.urls)),
    
    # Custom endpoints for conversations
    path('conversations/<uuid:conversation_id>/send-message/', 
         ConversationViewSet.as_view({'post': 'send_message'}), 
         name='conversation-send-message'),
    
    path('conversations/create/', 
         ConversationViewSet.as_view({'post': 'create_conversation'}), 
         name='create-conversation'),
    
    # Include default auth URLs
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
]