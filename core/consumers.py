# core/consumers.py
import logging

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from django.contrib.auth import authenticate
from django.db.models import Q

from core import models as messaging_models
from core import serializers
from core.models import User


class ChatConsumer(JsonWebsocketConsumer):

    def connect(self):
        """User connects to socket
         - channel is added to each thread group they are included in.
         - channel_name is added to the session so that it can be referenced later in views.py.
        """
        token = None
        for header in self.scope['headers']:
            if header[0] == b'authorization':
                token = str(header[1], 'utf-8').split(' ')[1].strip()
        if token:
            user = authenticate(token=token)
            if user and user.is_active:
                self.scope["user"] = user
                async_to_sync(
                    self.channel_layer.group_add)('all_users', self.channel_name)

                # # add connection to existing channel groups
                # for thread in messaging_models.Match.objects.filter(
                #         Q(user_1=self.scope["user"]) | Q(user_2=self.scope["user"])
                # ).values('hash_id').distinct():
                #         self.channel_layer.group_add)(thread['hash_id'], self.channel_name)
                # store client channel name in the user session

                self.scope['session']['channel_name'] = self.channel_name
                self.scope['session'].save()
                # accept client connection
                self.accept()

    def disconnect(self, close_code):
        """User is disconnected

         - user will leave all groups and the channel name is removed from the session.
        """
        # remove channel name from session
        if self.scope["user"].is_authenticated:
            if 'channel_name' in self.scope['session']:
                del self.scope['session']['channel_name']
                self.scope['session'].save()
            # async_to_sync(self.channel_layer.group_discard)(self.scope["user"].hash_id,
            #                                                 self.channel_name)

    def receive_json(self, content, **kwargs):
        """User sends a message
         - read all messages if data is read message
         - send message to thread and group socket if text message
         - Message is sent to the group associated with the message thread
         :param **kwargs:
        """
        if 'read' in content:
            logging.info(content)
            # client specifies they have read a message that was sent
            thread = messaging_models.Chat.objects.get(hash_id=str(content['read']))
            thread.mark_read(self.scope["user"])

        elif 'message' in content:
            logging.info(content)
            message = content['message']
            # extra security is added when we specify clients=p
            thread = messaging_models.Chat.objects.get(hash_id=message['id'])
            # forward chat message over group channel
            new_message = thread.add_message_text(message['text'], self.scope["user"])

            async_to_sync(self.channel_layer.group_send)(
                'all_users', {
                    "type": "chat.message",
                    "message": serializers.MessageSerializer(new_message, context={'user': self.scope["user"]}).data,
                }
            )

    def chat_message(self, event):
        """chat.message type"""
        message = event['message']
        logging.info(message)
        self.send_json(content=message)
