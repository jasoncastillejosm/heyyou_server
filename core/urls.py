# -*- coding: utf-8 -*-
from django.urls import path
from rest_framework import routers

from core import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'chats', views.ChatViewSet)

app_name = 'core'

urlpatterns = [
#     path('login', views.login),
#     path('logout', views.logout),
#     path('signup', views.signin),
]

urlpatterns = urlpatterns + router.urls
