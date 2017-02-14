# -*- coding: utf-8 -*-

from bothub_cli.api import Api


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


def fixture_api():
    transport = MockTransport()
    return transport, Api(transport=transport)


def record_token(transport):
    response = MockResponse({'data': {'access_token': 'testtoken'}})
    transport.record(response)


def test_authenticate_should_returns_token():
    transport, api = fixture_api()
    record_token(transport)
    token = api.authenticate('testuser', 'testpw')
    assert token == 'testtoken'
