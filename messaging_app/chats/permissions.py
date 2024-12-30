from rest_framework import permissions

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to access it.
    """
    def has_object_permission(self, request, view, obj):
        # Check if user is participant in the conversation
        if hasattr(obj, 'participants'):
            return request.user in obj.participants.all()
        # For messages, check the conversation
        elif hasattr(obj, 'conversation'):
            return request.user in obj.conversation.participants.all()
        return False

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated