# chats/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers as nested_routers
from .views import ConversationViewSet, MessageViewSet

# Initialize the default router
router = DefaultRouter()

# Register the main routes
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')

# Initialize the nested router
nested_router = nested_routers.NestedDefaultRouter(
    router,
    r'conversations',
    lookup='conversation'
)

# Register nested routes
nested_router.register(
    r'messages',
    MessageViewSet,
    basename='conversation-messages'
)

# Combine all URLs
urlpatterns = [
    path('', include(router.urls)),
    path('', include(nested_router.urls)),
]

# This will generate:
# /conversations/
# /conversations/{conversation_pk}/
# /conversations/{conversation_pk}/messages/
# /messages/
# /messages/{pk}/