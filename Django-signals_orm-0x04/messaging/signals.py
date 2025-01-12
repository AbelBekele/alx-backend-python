from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Message, Notification, MessageHistory

User = get_user_model()

@receiver(post_save, sender=Message)
def create_notification(sender, instance, created, **kwargs):
    """
    Signal to create a notification when a new message is created
    """
    if created:
        Notification.objects.create(
            user=instance.receiver,
            message=instance
        ) 

@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    if instance.id:  # Only if the message already exists (it's an edit)
        try:
            old_message = Message.objects.get(id=instance.id)
            # Only create history if content has changed
            if old_message.content != instance.content:
                # Get the current user from thread local storage
                from django.contrib.auth.models import AnonymousUser
                from django.db.models import F
                current_user = getattr(instance, '_current_user', None)
                
                MessageHistory.objects.create(
                    message=instance,
                    old_content=old_message.content,
                    edited_by=current_user  # Add the user who made the edit
                )
                instance.edited = True
        except Message.DoesNotExist:
            pass 

@receiver(post_delete, sender=User)
def cleanup_user_data(sender, instance, **kwargs):
    """
    Clean up all related data when a user is deleted.
    Note: If using CASCADE on foreign keys, this might not be necessary,
    but it's good practice to explicitly handle cleanup.
    """
    # Delete all messages sent by or received by the user
    Message.objects.filter(sender=instance).delete()
    Message.objects.filter(receiver=instance).delete()
    
    # Delete all notifications for the user
    Notification.objects.filter(user=instance).delete()
    
    # Delete all message histories edited by the user
    MessageHistory.objects.filter(edited_by=instance).delete() 