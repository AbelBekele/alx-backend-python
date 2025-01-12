from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

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