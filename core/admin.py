# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.admin import register
from django.contrib.auth.admin import UserAdmin as UserBaseAdmin

from core.models import User, Chat, Message, UnreadReceipt


@register(User)
class UserAdmin(UserBaseAdmin):
    pass


@register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('hash_id', 'title', 'author', 'timestamp', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title',)


@register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('hash_id', 'text', 'sender', 'timestamp')
    search_fields = ('text',)


@register(UnreadReceipt)
class UnreadReceiptAdmin(admin.ModelAdmin):
    list_display = ('thread', 'recipient', 'message', 'is_sent')
    list_filter = ('is_sent',)
