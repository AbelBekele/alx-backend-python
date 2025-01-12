from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Q
from .managers import UnreadMessagesManager

User = get_user_model()

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)
    parent_message = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    read = models.BooleanField(default=False)
    
    # Add the custom manager while keeping the default manager
    objects = models.Manager()
    unread = UnreadMessagesManager()
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f'{self.sender} to {self.receiver}: {self.content[:50]}'
    
    def mark_as_read(self):
        """Mark a single message as read"""
        if not self.read:
            self.read = True
            self.save(update_fields=['read'])
    
    def get_thread(self):
        """Get all messages in the thread, including parent and replies"""
        if self.parent_message:
            return self.parent_message.get_thread()
        return Message.objects.filter(
            models.Q(id=self.id) | models.Q(parent_message=self)
        ).select_related('sender', 'receiver', 'parent_message')

class MessageHistory(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='history')
    old_content = models.TextField()
    edited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    edited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-edited_at']
        verbose_name_plural = "Message histories"

    def __str__(self):
        editor = self.edited_by.username if self.edited_by else "Unknown"
        return f'Edited by {editor} at {self.edited_at}'

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Notification for {self.user} - Message from {self.message.sender}" 