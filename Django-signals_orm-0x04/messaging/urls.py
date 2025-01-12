from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('messages/', views.message_list, name='message_list'),
    path('messages/thread/<int:message_id>/', views.message_thread, name='message_thread'),
    path('messages/send/', views.send_message, name='send_message'),
    path('conversations/', views.user_conversations, name='conversations'),
] 