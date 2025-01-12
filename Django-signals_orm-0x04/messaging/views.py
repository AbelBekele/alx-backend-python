from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import logout
from django.contrib import messages

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