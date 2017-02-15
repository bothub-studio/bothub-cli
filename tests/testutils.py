# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)


class MockTransport(object):
    def __init__(self):
        self.buf = []

    def record(self, data):
        self.buf.append(data)

    def post(self, *args, **kwargs):
        return self.buf.pop(0)

    def get(self, *args, **kwargs):
        return self.buf.pop(0)

    def put(self, *args, **kwargs):
        return self.buf.pop(0)


class MockResponse(object):
    def __init__(self, body, status_code=200):
        self.body = body
        self.status_code = status_code

    def json(self):
        return self.body


