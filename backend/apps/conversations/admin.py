from django.contrib import admin
from .models import Conversation, Message


class MessageInline(admin.TabularInline):
    model = Message
    fields = ('direction', 'sender_name', 'content', 'sent_at', 'reply_interval')
    readonly_fields = fields
    ordering = ('sent_at',)
    max_num = 50


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('platform', 'shop_name', 'customer_name', 'employee',
                    'status', 'total_deduction', 'risk_level', 'started_at')
    list_filter = ('platform', 'status', 'risk_level', 'tenant')
    search_fields = ('customer_name', 'conversation_id', 'shop_name')
    inlines = [MessageInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'direction', 'sender_name', 'sent_at', 'reply_interval')
    list_filter = ('direction',)
    search_fields = ('content',)