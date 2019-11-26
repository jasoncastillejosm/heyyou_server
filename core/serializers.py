# -*- coding: utf-8 -*-
from rest_framework import serializers

from core.models import User, Chat, Message, UnreadReceipt


class UserSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='hash_id', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name')


class MessageSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='hash_id', read_only=True)
    sender_id = serializers.CharField(source='sender.hash_id', read_only=True)
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    thread_id = serializers.CharField(source='thread.hash_id', read_only=True)
    is_me = serializers.SerializerMethodField('_is_me')

    class Meta:
        model = Message
        fields = ('id', 'is_me', 'timestamp', 'text', 'sender_id', 'sender_name', 'thread_id')

    def _is_me(self, obj):
        if self.context['user'] == obj.sender:
            return True
        return False


class MessageListSerializer(serializers.ListSerializer):
    child = MessageSerializer()
    many = True
    allow_null = True


class ChatSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='hash_id', read_only=True)
    unread_count = serializers.SerializerMethodField('_unread_count')
    last_message = serializers.CharField(source='last_message.text', read_only=True)
    # TODO: last_message = MessageSerializer(many=False, allow_null=True)
    author = UserSerializer(read_only=True, many=False)
    #title = serializers.CharField(default="(empty)", read_only=True)

    class Meta:
        model = Chat
        fields = ('id', 'title', 'last_message', 'unread_count', 'author')

    def _unread_count(self, obj):
        return UnreadReceipt.objects.filter(
            recipient=self.context['user'], message__chat=obj
        ).exists()


class ChatListSerializer(serializers.ModelSerializer):
    # child = ChatSerializer()
    # many = True
    # allow_null = True

    id = serializers.CharField(source='hash_id', read_only=True)
    unread_count = serializers.SerializerMethodField('_unread_count')
    last_message = serializers.CharField(source='last_message.text', read_only=True)
    last_message_author = serializers.SerializerMethodField('_get_last_message_author')
    user = UserSerializer(read_only=True, many=False)

    class Meta:
        model = Chat
        fields = (
            'id', 'title', 'unread_count', 'last_message', 'last_message_author', 'user',
        )

    def _get_last_message_author(self, obj):
        if obj.last_message:
            return obj.last_message.sender_id
        return None

    def _unread_count(self, obj):
        return UnreadReceipt.objects.filter(
            recipient=self.context['user'], message__chat=obj
        ).exists()


