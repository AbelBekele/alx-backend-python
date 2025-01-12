from django.contrib import admin
from .models import Message, Notification, MessageHistory

class MessageHistoryInline(admin.TabularInline):
    model = MessageHistory
    readonly_fields = ('old_content', 'edited_at', 'edited_by')
    extra = 0
    can_delete = False

class RepliesInline(admin.TabularInline):
    model = Message
    fk_name = 'parent_message'
    readonly_fields = ('sender', 'receiver', 'content', 'timestamp', 'edited')
    extra = 0
    can_delete = False
    verbose_name = "Reply"
    verbose_name_plural = "Replies"

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'content', 'timestamp', 'edited', 'is_reply', 'read')
    list_filter = ('sender', 'receiver', 'timestamp', 'edited', 'read')
    search_fields = ('content', 'sender__username', 'receiver__username')
    inlines = [MessageHistoryInline, RepliesInline]
    raw_id_fields = ('parent_message',)
    actions = ['mark_as_read', 'mark_as_unread']

    def is_reply(self, obj):
        return bool(obj.parent_message)
    is_reply.boolean = True
    is_reply.short_description = "Is Reply"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'sender', 'receiver', 'parent_message'
        )
    
    def mark_as_read(self, request, queryset):
        queryset.update(read=True)
    mark_as_read.short_description = "Mark selected messages as read"
    
    def mark_as_unread(self, request, queryset):
        queryset.update(read=False)
    mark_as_unread.short_description = "Mark selected messages as unread"

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'read', 'created_at')
    list_filter = ('read', 'created_at')
    search_fields = ('user__username',)

@admin.register(MessageHistory)
class MessageHistoryAdmin(admin.ModelAdmin):
    list_display = ('message', 'old_content', 'edited_by', 'edited_at')
    list_filter = ('edited_at', 'edited_by')
    search_fields = ('message__content', 'old_content', 'edited_by__username')
    readonly_fields = ('message', 'old_content', 'edited_at', 'edited_by') 