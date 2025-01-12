from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Message, Notification, MessageHistory

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