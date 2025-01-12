from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('messages/', views.message_list, name='message_list'),
    path('messages/thread/<int:message_id>/', views.message_thread, name='message_thread'),
    path('messages/send/', views.send_message, name='send_message'),
    path('conversations/', views.user_conversations, name='conversations'),
    path('messages/unread/', views.unread_messages, name='unread_messages'),
    path('messages/mark-read/', views.mark_messages_read, name='mark_messages_read'),
    path('messages/<int:message_id>/', views.message_detail, name='message_detail'),
] 