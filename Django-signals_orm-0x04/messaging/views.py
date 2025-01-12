from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import logout
from django.contrib import messages
from django.db.models import Q, Prefetch
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache
from .models import Message, Notification
from django.http import JsonResponse

@login_required
def edit_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    
    # Check if user has permission to edit
    if message.sender != request.user:
        return HttpResponseForbidden("You can't edit this message")
    
    if request.method == 'POST':
        new_content = request.POST.get('content')
        if new_content and new_content != message.content:
            message.content = new_content
            # Set the current user before saving
            message._current_user = request.user
            message.save()
    
    return redirect('message_detail', message_id=message.id) 

@login_required
def delete_user(request):
    if request.method == 'POST':
        user = request.user
        # Logout the user before deletion to avoid any session issues
        logout(request)
        # The actual deletion of related data will be handled by signals
        user.delete()
        messages.success(request, 'Your account has been successfully deleted.')
        return redirect('login')
    return redirect('profile')  # Redirect to profile page if not a POST request 

@login_required
@cache_page(60)  # Cache for 60 seconds
def message_list(request):
    """
    Display messages for the current user with optimized queries
    """
    cache_key = f'message_list_{request.user.id}'
    cached_messages = cache.get(cache_key)
    
    if cached_messages is None:
        messages = Message.objects.filter(
            Q(sender=request.user) | Q(receiver=request.user),
            parent_message__isnull=True  # Only get top-level messages
        ).select_related(
            'sender', 
            'receiver'
        ).only(
            'sender__username',
            'receiver__username',
            'content',
            'timestamp',
            'edited',
            'read',
            'id',
            'sender_id',
            'receiver_id'
        ).prefetch_related(
            Prefetch(
                'replies',
                queryset=Message.objects.select_related('sender', 'receiver').only(
                    'sender__username',
                    'receiver__username',
                    'content',
                    'timestamp',
                    'edited',
                    'read',
                    'id',
                    'sender_id',
                    'receiver_id',
                    'parent_message_id'
                )
            )
        ).order_by('-timestamp')
        
        cache.set(cache_key, messages, 60)  # Cache for 60 seconds
    else:
        messages = cached_messages

    return render(request, 'messaging/message_list.html', {'messages': messages})

@login_required
@cache_page(60)  # Cache for 60 seconds
def message_thread(request, message_id):
    """
    Display a complete message thread with all replies
    """
    cache_key = f'message_thread_{message_id}'
    cached_data = cache.get(cache_key)
    
    if cached_data is None:
        message = get_object_or_404(
            Message.objects.select_related('sender', 'receiver'),
            id=message_id
        )
        
        thread = message.get_thread().prefetch_related(
            'history',
            'history__edited_by'
        )
        
        cached_data = {
            'thread': thread,
            'root_message': message
        }
        cache.set(cache_key, cached_data, 60)
    
    return render(request, 'messaging/message_thread.html', cached_data)

@login_required
@cache_page(60)  # Cache for 60 seconds
def user_conversations(request):
    """
    Display all conversations for the current user
    """
    cache_key = f'user_conversations_{request.user.id}'
    cached_data = cache.get(cache_key)
    
    if cached_data is None:
        conversations = Message.objects.filter(
            Q(sender=request.user) | Q(receiver=request.user)
        ).select_related(
            'sender',
            'receiver'
        ).only(
            'sender__username',
            'receiver__username',
            'content',
            'timestamp',
            'id',
            'sender_id',
            'receiver_id'
        ).order_by('timestamp').distinct()

        # Group messages by conversation partner
        grouped_conversations = {}
        for message in conversations:
            partner = message.receiver if message.sender == request.user else message.sender
            if partner not in grouped_conversations:
                grouped_conversations[partner] = []
            grouped_conversations[partner].append(message)
            
        cached_data = {'conversations': grouped_conversations}
        cache.set(cache_key, cached_data, 60)

    return render(request, 'messaging/conversations.html', cached_data)

@login_required
def unread_messages(request):
    """
    Display unread messages for the current user
    """
    unread = Message.unread.unread_for_user(request.user)
    return render(request, 'messaging/unread_messages.html', {'messages': unread})

@login_required
def mark_messages_read(request):
    """
    Mark multiple messages as read
    """
    if request.method == 'POST':
        message_ids = request.POST.getlist('message_ids')
        Message.unread.mark_as_read(message_ids, request.user)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def message_detail(request, message_id):
    """
    Display a message and mark it as read
    """
    message = get_object_or_404(
        Message.objects.select_related('sender', 'receiver').only(
            'sender__username',
            'receiver__username',
            'content',
            'timestamp',
            'edited',
            'read',
            'id',
            'sender_id',
            'receiver_id'
        ),
        id=message_id
    )
    
    # Mark message as read if the current user is the receiver
    if message.receiver == request.user and not message.read:
        message.mark_as_read()
    
    return render(request, 'messaging/message_detail.html', {'message': message}) 

# Function to invalidate cache when messages are modified
def invalidate_message_caches(user_id, message_id=None):
    """Helper function to invalidate relevant caches when messages change"""
    cache.delete(f'message_list_{user_id}')
    cache.delete(f'user_conversations_{user_id}')
    if message_id:
        cache.delete(f'message_thread_{message_id}')

@login_required
@cache_page(60)  # Cache for 60 seconds
def send_message(request):
    """
    Send a new message or reply to an existing message
    """
    if request.method == 'POST':
        content = request.POST.get('content')
        receiver_id = request.POST.get('receiver')
        parent_message_id = request.POST.get('parent_message')
        
        message = Message.objects.create(
            sender=request.user,
            receiver_id=receiver_id,
            content=content,
            parent_message_id=parent_message_id if parent_message_id else None
        )
        
        # Invalidate relevant caches
        invalidate_message_caches(request.user.id)
        invalidate_message_caches(receiver_id)
        
        thread = message.get_thread().select_related(
            'sender',
            'receiver',
            'parent_message'
        )
        
        return render(request, 'messaging/message_thread.html', {'thread': thread})
    
    return render(request, 'messaging/send_message.html') 