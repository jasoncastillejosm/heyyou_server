# HeyYou

Simple real time chat Django app backend with RESTApi framework and django 
channels for socket connection. (core app)

Django 2 and python 3

# Api

Api in DjangoRestFramework and access with Token (channel and api) set with routers.

## Endpoints

Api urls starts with /api. All in core.urls and core.views

## Socket django channel

To start socket connection, install Redis server is needed.

Install Mac OS: brew install redis

Start service from terminal

```bash
    redis-server /usr/local/etc/redis.conf
```
