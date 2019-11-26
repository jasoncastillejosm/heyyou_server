# -*- coding: utf-8 -*-
import datetime

from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login as user_login, logout as user_logout
from django.contrib.auth import authenticate

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from core import serializers
from core import utils
from core.models import User, Chat, Message
from core.serializers import UserSerializer, ChatSerializer, ChatListSerializer, MessageSerializer, MessageListSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_staff=False, is_superuser=False)
    serializer_class = UserSerializer
    list_serializer_class = UserSerializer  # UserListSerializer

    def get_object(self):
        if self.kwargs['pk'] == 'me':
            self.kwargs['pk'] = self.request.user.pk
        return super(UserViewSet, self).get_object()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_queryset().get(hash_id=kwargs.get('pk'))
        serializer = UserSerializer(instance, context={'user': request.user})
        data = utils.response_dictionary(1, '', serializer.data)
        return JsonResponse(data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False, permission_classes=[AllowAny])
    def register(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if User.objects.filter(username=username).exists():
            return JsonResponse(
                utils.response_dictionary(0, "Ya existe", None),
                status=status.HTTP_401_UNAUTHORIZED
            )
        user = User.objects.create(username=username)
        user.set_password(password)
        user.first_name = username
        user.save()

        results = {
            'token': user.get_token(),
            'profile': UserSerializer(user).data,
        }
        data = utils.response_dictionary(1, u'OK', results)
        return JsonResponse(data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False, permission_classes=[AllowAny])
    def login(self, request):
        token = None
        user = None
        data = utils.response_dictionary(0, u'Los datos de acceso no son válidos.', {})

        try:
            user = User.objects.get(username=request.data['username'])
            if user and user.check_password(request.data['password']):
                token = user.get_token()
            else:
                data = utils.response_dictionary(0, u'Los datos de acceso son incorrectos', {})
        except User.DoesNotExist:
            data = utils.response_dictionary(0, u'Los datos de acceso son incorrectos', {})

        if token:
            if not user.is_active:
                data = utils.response_dictionary(
                    0,
                    u'Cuenta dada de baja. Contactar con admin para reactivarla',
                    {}
                )
                return JsonResponse(data, status=status.HTTP_200_OK)

            results = {
                'token': token,
                'profile': UserSerializer(user).data,
            }

            data = utils.response_dictionary(1, u'Login realizado', results)

        return JsonResponse(data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def logout(self, request):
        user_logout(request)
        return JsonResponse(
            utils.response_dictionary(1, 'OK', {}),
            status=status.HTTP_200_OK
        )


class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.filter(is_active=True)
    serializer_class = ChatSerializer
    list_serializer_class = ChatListSerializer

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), hash_id=self.kwargs.get('pk'))
        #get_object_or_404(self.get_queryset(), **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def filter_queryset(self, queryset):
        return queryset

    def list(self, request, *args, **kwargs):
        now = datetime.datetime.now()
        queryset = self.filter_queryset(self.get_queryset())
        serializer = ChatListSerializer(queryset, many=True,
                                   context={'user': request.user}
                                  ).data
        _dict = utils.response_dictionary(1, u'OK', serializer)
        return JsonResponse(_dict, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):

        try:
            chat = self.get_object()  # Chat.objects.get(hash_id=kwargs.get('pk'))
            chat.mark_read(request.user)
        except Chat.DoesNotExist:
            data = utils.response_dictionary(0, 'NOK', {})
            return JsonResponse(data, status=status.HTTP_401_UNAUTHORIZED)

        q = [Q(thread=chat)]
        if 'before' in request.GET:
            q.append(Q(date__lt=int(request.GET['before'])))

        messages = Message.objects.filter(*q).order_by('timestamp')
        count = messages.count() - 30 if messages.count() > 30 else 0
        messages_data = MessageListSerializer(messages[count:],
                                              context={'user': self.request.user}).data
        chat_serializer = ChatSerializer(chat, context={'user': request.user})
        d = {
            'messages': messages_data,
            'messages_end': messages.count() <= 30
        }
        d.update(chat_serializer.data)
        data = utils.response_dictionary(1, '', d)
        return JsonResponse(data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        request.data._mutable = True
        request.data['author'] = self.request.user.id
        serializer = ChatSerializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = utils.response_dictionary(1, u'Created', serializer.data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    @action(methods=['POST'], detail=True)
    def message(self, request, pk=None):
        instance = self.get_object()
        message = Message.objects.create(thread=instance,
                                         text=request.data['message'],
                                         sender=self.request.user)
        instance.messages.add(message)
        instance.last_message = message
        instance.save()
        serializer = MessageSerializer(message, context={'user': self.request.user})
        data = utils.response_dictionary(1, u'Created', serializer.data)
        return JsonResponse(data, status=status.HTTP_201_CREATED)
