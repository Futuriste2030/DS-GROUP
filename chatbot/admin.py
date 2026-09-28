from django.contrib import admin
from django.db import models
from ckeditor.widgets import CKEditorWidget
from .models import ChatbotKnowledge, Conversation, Message


@admin.register(ChatbotKnowledge)
class ChatbotKnowledgeAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'updated_at']
    list_filter = ['is_active']
    search_fields = ['name', 'content']
    readonly_fields = ['updated_at']
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget},
    }


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ['role', 'content', 'created_at']
    can_delete = False
    fields = ['role', 'content', 'created_at']


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'created_at', 'updated_at']
    search_fields = ['session_id']
    inlines = [MessageInline]
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'role', 'content_short', 'created_at']
    list_filter = ['role']
    search_fields = ['content']

    def content_short(self, obj):
        return obj.content[:80]
    content_short.short_description = 'Content'
