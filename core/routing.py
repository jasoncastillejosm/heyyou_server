# -*- coding: utf-8 -*-
from django.urls import path

from core import consumers

websocket_urlpatterns = [
    path('connect', consumers.ChatConsumer),
]