# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework.authtoken.models import Token

from core import utils


class User(AbstractUser):
    """Extends User model from Django"""
    hash_id = models.CharField('id', max_length=32, default=utils.create_hash, unique=True)

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def get_token(self):
        try:
            return self.auth_token.key
        except Token.DoesNotExist:
            return Token.objects.create(user=self).key


class Chat(models.Model):
    hash_id = models.CharField('id', max_length=32, default=utils.create_hash, unique=True)
    title = models.CharField('Title', max_length=32)
    last_message = models.ForeignKey('Message', verbose_name=u'Last message', on_delete=models.CASCADE, null=True, blank=True)
    timestamp = models.IntegerField(default=utils.time_stamp)
    author = models.ForeignKey('core.User', help_text='Author of this chat', on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField('Active', help_text='Is this chat available', default=True)

    def __str__(self):
        return "{}".format(self.title)

    class Meta:
        verbose_name = 'Chat'
        verbose_name_plural = 'Chats'

    def mark_read(self, user):
        UnreadReceipt.objects.filter(recipient=user, thread=self).delete()

    def add_message_text(self, text, sender):
        """User sends text to the chat
         - creates new message with foreign key to self
         - adds unread receipt for each user
         - returns instance of new message
        """
        new_message = Message(text=text, sender=sender, thread=self)
        new_message.save()

        self.last_message = new_message
        self.save()

        #if self.user_1_id == sender.id:
        #    UnreadReceipt.objects.create(recipient=self.user_2, thread=self, message=new_message)
        #elif self.user_2_id == sender.id:
         #   UnreadReceipt.objects.create(recipient=self.user_1, thread=self, message=new_message)
        # for c in self.clients.exclude(id=sender.id):
        #     UnreadReceipt.objects.create(recipient=c, thread=self, message=new_message)
        return new_message

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        is_new = not self.id
        super().save(force_insert, force_update, using, update_fields)


class Message(models.Model):
    """Thread Message

     - An unread receipt is created for each recipient in the related thread
    """
    hash_id = models.CharField(max_length=32, default=utils.create_hash, unique=True)
    timestamp = models.IntegerField(default=utils.time_stamp)
    text = models.CharField('Message', max_length=1024)
    thread = models.ForeignKey('Chat', verbose_name='Chat', on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey('User', verbose_name='User', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return "{}".format(self.hash_id)

    class Meta:
        verbose_name = 'Mensaje'
        verbose_name_plural = 'Mensajes'


class UnreadReceipt(models.Model):
    """Unread receipt for unread messages

    Consists of:
     - date sent integer timestamp
     - ForeignKey to corresponding Message
     - ForeignKey to Thread
     - ForeignKey to User who has not yet seen message

    Brief:
     - deleted when a user loads thread messages or when they respond with
       the 'read' message over websocket connection
    """
    date = models.IntegerField(default=utils.time_stamp)
    message = models.ForeignKey('Message', on_delete=models.CASCADE, related_name='receipts')
    thread = models.ForeignKey('Chat', on_delete=models.CASCADE, related_name='receipts')
    recipient = models.ForeignKey('User', on_delete=models.CASCADE, related_name='receipts')
    is_sent = models.BooleanField('Push sent', default=False)

    # def send_message_notification(self):
    #     for device in GCMDevice.objects.filter(user=self.recipient, active=True):
    #         logging.info(
    #             u'send_message_notification recipient={}; device={}; message={}'
    #                 .format(self.recipient, device.id, self.id)
    #         )
    #     # for device in GCMDevice.objects.filter(user=self.recipient, active=True):
    #         self.is_sent = True
    #         self.save()
    #         try:
    #             data = {
    #                 "_title": self.message.sender.first_name,
    #                 "msg": self.message.text,
    #                 "timestamp": '%s' % datetime.datetime.now(),
    #                 'chat_hash_id': self.message.chat.hash_id,
    #                 'message_hash_id': self.message.hash_id,
    #             }
    #             if device.name != 'android':
    #                 data.update({
    #                     'title': self.message.sender.first_name,
    #                     'body': self.message.text,
    #                     'sound': 'default',
    #                 })
    #             device.send_message(None, extra=data)
    #         except Exception as e:
    #             # client.captureException()
    #             # logging.info(u'send_message_notification: {}'.format(e.message))
    #             device.active = False
    #             device.save()
