from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import logout
from django.contrib import messages
from django.db.models import Q, Prefetch
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
def message_list(request):
    """
    Display messages for the current user with optimized queries
    """
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

    return render(request, 'messaging/message_list.html', {'messages': messages})

@login_required
def message_thread(request, message_id):
    """
    Display a complete message thread with all replies
    """
    # Get the root message of the thread
    message = get_object_or_404(
        Message.objects.select_related('sender', 'receiver'),
        id=message_id
    )
    
    # Get the complete thread
    thread = message.get_thread().prefetch_related(
        'history',
        'history__edited_by'
    )

    return render(request, 'messaging/message_thread.html', {
        'thread': thread,
        'root_message': message
    })

@login_required
def send_message(request):
    """
    Send a new message or reply to an existing message
    """
    if request.method == 'POST':
        content = request.POST.get('content')
        receiver_id = request.POST.get('receiver')
        parent_message_id = request.POST.get('parent_message')
        
        # Create new message with optimized query
        message = Message.objects.create(
            sender=request.user,
            receiver_id=receiver_id,
            content=content,
            parent_message_id=parent_message_id if parent_message_id else None
        )
        
        # Get the complete thread with optimized query
        thread = message.get_thread().select_related(
            'sender',
            'receiver',
            'parent_message'
        )
        
        return render(request, 'messaging/message_thread.html', {'thread': thread})
    
    return render(request, 'messaging/send_message.html')

@login_required
def user_conversations(request):
    """
    Display all conversations for the current user
    """
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

    return render(request, 'messaging/conversations.html', {
        'conversations': grouped_conversations
    })

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