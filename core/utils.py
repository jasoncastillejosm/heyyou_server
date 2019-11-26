# -*- coding: utf-8 -*-
import os
import time

from binascii import hexlify

from django.conf import settings
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.utils.urls import replace_query_param


def get_full_url_from_request(request):
    meta = request.META
    path = ''
    if 'PATH_INFO' in meta and 'HTTP_HOST' in meta and 'wsgi.url_scheme':
        # TODO: meta['wsgi.url_scheme'] Does not exist
        path = 'http' + '://' + meta['HTTP_HOST'] + meta['PATH_INFO']

    return path


class PaginatorModels(PageNumberPagination):

    def __init__(self, *args, **kwargs):
        if kwargs.get("page_size"):
            self.page_size = kwargs.pop("page_size")
        super(PaginatorModels, self).__init__(*args, **kwargs)

    def get_paginated_response(self, data, status=None, msg=None, extra=None):
        if not self.page_size:
            self.page_size = settings.REST_FRAMEWORK['PAGE_SIZE']
        return Response({'count': self.page.paginator.count,
                         'current': self.page.number,
                         'pages': ((self.page.paginator.count - 1) // self.page_size) + 1,
                         'next': self.get_next_link(),
                         'prev': self.get_previous_link(),
                         'results': data,
                         'status': status,
                         'msg': msg,
                         'extra': extra})

    def get_next_link(self):
        if not self.page.has_next():
            return None

        url = self.get_full_url() + "?" + self.request.GET.urlencode()
        page_number = self.page.next_page_number()
        return replace_query_param(url, self.page_query_param, page_number)

    def get_previous_link(self):
        if not self.page.has_previous():
            return None

        url = self.get_full_url() + "?" + self.request.GET.urlencode()
        page_number = self.page.previous_page_number()
        return replace_query_param(url, self.page_query_param, page_number)

    def get_full_url(self):
        return get_full_url_from_request(self.request)


def create_hash():
    return str(hexlify(os.urandom(16)), 'ascii')


def time_stamp():
    return int(round(time.time()))


def response_dictionary(status=None, msg=None, results=None, extra=None):
    """
    Generamos los diferentes valores de la request a devolver para todas las apis
    """
    data = {}
    if status is not None and msg is not None and results is not None:
        data = {
            'status': status,
            'msg': msg,
            'results': results,
            'extra': extra
        }

    return data
