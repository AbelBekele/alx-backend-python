from django.db import models
from django.db.models import Q

class UnreadMessagesManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()
    
    def unread_for_user(self, user):
        """Get unread messages for a specific user with optimized query"""
        return self.get_queryset().filter(
            receiver=user,
            read=False
        ).select_related(
            'sender'
        ).only(
            'sender__username',
            'content',
            'timestamp',
            'read',
            'id',  # Always include primary key
            'sender_id'  # Include foreign key for optimization
        )
    
    def mark_as_read(self, message_ids, user):
        """Mark multiple messages as read for a user"""
        return self.get_queryset().filter(
            id__in=message_ids,
            receiver=user,
            read=False
        ).update(read=True) 