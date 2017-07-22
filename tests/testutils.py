# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)


class MockTransport(object):
    def __init__(self):
        self.response = []
        self.called = []

    def record(self, data):
        self.response.append(data)

    def post(self, *args, **kwargs):
        self.called.append(('post', args, kwargs))
        return self.response.pop(0)

    def get(self, *args, **kwargs):
        self.called.append(('get', args, kwargs))
        return self.response.pop(0)

    def put(self, *args, **kwargs):
        self.called.append(('put', args, kwargs))
        return self.response.pop(0)

    def delete(self, *args, **kwargs):
        self.called.append(('delete', args, kwargs))
        return self.response.pop(0)


class MockResponse(object):
    def __init__(self, body, status_code=200):
        self.body = body
        self.status_code = status_code

    def json(self):
        return self.body
