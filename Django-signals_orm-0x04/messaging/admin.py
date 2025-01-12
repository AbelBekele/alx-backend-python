from django.contrib import admin
from .models import Message, Notification, MessageHistory

class MessageHistoryInline(admin.TabularInline):
    model = MessageHistory
    readonly_fields = ('old_content', 'edited_at')
    extra = 0
    can_delete = False

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'content', 'timestamp', 'edited')
    list_filter = ('sender', 'receiver', 'timestamp', 'edited')
    search_fields = ('content', 'sender__username', 'receiver__username')
    inlines = [MessageHistoryInline]

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'read', 'created_at')
    list_filter = ('read', 'created_at')
    search_fields = ('user__username',)

@admin.register(MessageHistory)
class MessageHistoryAdmin(admin.ModelAdmin):
    list_display = ('message', 'old_content', 'edited_at')
    list_filter = ('edited_at',)
    search_fields = ('message__content', 'old_content')
    readonly_fields = ('message', 'old_content', 'edited_at') 