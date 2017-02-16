# -*- coding: utf-8 -*-

from bothub_cli.api import Api
from .testutils import MockResponse
from .testutils import MockTransport


def fixture_api():
    transport = MockTransport()
    api = Api(transport=transport)
    config = {'auth_token': 'testtoken'}
    api.load_auth(config)
    return transport, api


def record_token(transport):
    data = {'data': {'access_token': 'testtoken'}}
    response = MockResponse(data)
    transport.record(response)


def record_project(transport):
    data = {'data': {'id': 1, 'name': 'testproject', 'short_name': 'testproject'}}
    response = MockResponse(data, status_code=201)
    transport.record(response)


def test_authenticate_should_returns_token():
    transport, api = fixture_api()
    record_token(transport)
    token = api.authenticate('testuser', 'testpw')
    assert token == 'testtoken'


def test_create_project_should_returns_project():
    transport, api = fixture_api()
    record_project(transport)
    project = api.create_project('testproject')
    assert project['name'] == 'testproject'
    assert project['id'] == 1
