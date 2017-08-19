# -*- coding: utf-8 -*-

import os
from bothub_cli.api import Api
from .testutils import MockResponse
from .testutils import MockTransport


def fixture_api():
    transport = MockTransport()
    api = Api(base_url='', transport=transport, verify_token_expire=False)
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


def record_true(transport):
    data = {'data': True}
    response = MockResponse(data, status_code=200)
    transport.record(response)


def test_authenticate_should_returns_token():
    transport, api = fixture_api()
    record_token(transport)
    token = api.authenticate('testuser', 'testpw')
    assert token == 'testtoken'


def test_list_project_should_construct_request():
    transport, api = fixture_api()
    record_true(transport)
    response = api.list_projects()
    assert response is True

    called = transport.called[0]
    assert called == (
        'get',
        ('/users/self/projects', ),
        {
            'headers': {'Authorization': 'Bearer testtoken'}
        }
    )


def test_create_project_should_construct_request():
    transport, api = fixture_api()
    record_true(transport)
    response = api.create_project('testproject', '')
    assert response is True

    called = transport.called[0]
    assert called == (
        'post',
        ('/projects', ),
        {
            'json': {
                'name': 'testproject',
                'short_name': 'testproject',
                'description': '',
            },
            'headers': {'Authorization': 'Bearer testtoken'}
        }
    )


def test_get_project_should_construct_request():
    transport, api = fixture_api()
    record_true(transport)
    response = api.get_project(1)
    assert response is True

    called = transport.called[0]
    assert called == (
        'get',
        ('/projects/1', ),
        {
            'headers': {'Authorization': 'Bearer testtoken'}
        }
    )


def test_delete_project_should_construct_request():
    transport, api = fixture_api()
    record_true(transport)
    api.delete_project(1)

    called = transport.called[0]
    assert called == (
        'delete',
        ('/projects/1', ),
        {
            'headers': {'Authorization': 'Bearer testtoken'}
        }
    )


def test_add_project_channel_should_construct_request():
    transport, api = fixture_api()
    record_true(transport)
    response = api.add_project_channel(1, 'mychannel', {'api_key': 'mykey'})
    assert response is True

    called = transport.called[0]
    assert called == (
        'post',
        ('/projects/1/channels/mychannel', ),
        {
            'json': {
                'credentials': {'api_key': 'mykey'},
            },
            'headers': {'Authorization': 'Bearer testtoken'}
        }
    )


def test_get_project_channels_should_construct_request():
    transport, api = fixture_api()
    record_true(transport)
    response = api.get_project_channels(1)
    assert response is True

    called = transport.called[0]
    assert called == (
        'get',
        ('/projects/1/channels', ),
        {
            'headers': {'Authorization': 'Bearer testtoken'}
        }
    )


def test_delete_project_channels_should_construct_request():
    transport, api = fixture_api()
    record_true(transport)
    api.delete_project_channels(1, 'mychannel')

    called = transport.called[0]
    assert called == (
        'delete',
        ('/projects/1/channels/mychannel', ),
        {
            'headers': {'Authorization': 'Bearer testtoken'}
        }
    )


def test_upload_code_should_construct_request_only_with_language():
    transport, api = fixture_api()
    record_true(transport)
    response = api.upload_code(1, 'python')
    assert response is True

    called = transport.called[0]
    assert called == (
        'post',
        ('/projects/1/bot', ),
        {
            'data': {'language': 'python'},
            'files': None,
            'headers': {'Authorization': 'Bearer testtoken'}
        }
    )


def test_upload_code_should_construct_request_with_language_and_code():
    transport, api = fixture_api()
    record_true(transport)
    response = api.upload_code(1, 'python', 'myfile')
    assert response is True

    called = transport.called[0]
    assert called == (
        'post',
        ('/projects/1/bot', ),
        {
            'data': {'language': 'python'},
            'files': {'code': 'myfile'},
            'headers': {'Authorization': 'Bearer testtoken'}
        }
    )


def test_get_code_should_construct_request():
    transport, api = fixture_api()
    record_true(transport)
    response = api.get_code(1)
    assert response is True

    called = transport.called[0]
    assert called == (
        'get',
        ('/projects/1/bot', ),
        {
            'headers': {'Authorization': 'Bearer testtoken'}
        }
    )


def test_set_project_property_should_construct_request():
    transport, api = fixture_api()
    record_true(transport)
    response = api.set_project_property(1, 'mykey', 'myval')
    assert response is True

    called = transport.called[0]
    assert called == (
        'post',
        ('/projects/1/properties', ),
        {
            'json': {'data': {'mykey': 'myval'}},
            'headers': {'Authorization': 'Bearer testtoken'}
        }
    )


def test_get_project_property_should_construct_request():
    transport, api = fixture_api()
    record_true(transport)
    response = api.get_project_property(1)
    assert response is True

    called = transport.called[0]
    assert called == (
        'get',
        ('/projects/1/properties', ),
        {
            'headers': {'Authorization': 'Bearer testtoken'}
        }
    )


def test_delete_project_property_should_construct_request():
    transport, api = fixture_api()
    record_true(transport)
    api.delete_project_property(1, 'mykey')

    called = transport.called[0]
    assert called == (
        'delete',
        ('/projects/1/properties/mykey', ),
        {
            'headers': {'Authorization': 'Bearer testtoken'}
        }
    )


def test_add_project_nlu_should_construct_request():
    transport, api = fixture_api()
    record_true(transport)
    response = api.add_project_nlu(1, 'apiai', {'apikey': 'mykey'})
    assert response is True

    called = transport.called[0]
    assert called == (
        'post',
        ('/projects/1/nlus', ),
        {
            'json': {'nlu': 'apiai', 'credentials': {'apikey': 'mykey'}},
            'headers': {'Authorization': 'Bearer testtoken'}
        }
    )


def test_get_project_nlus_should_construct_request():
    transport, api = fixture_api()
    record_true(transport)
    response = api.get_project_nlus(1)
    assert response is True

    called = transport.called[0]
    assert called == (
        'get',
        ('/projects/1/nlus', ),
        {
            'headers': {'Authorization': 'Bearer testtoken'}
        }
    )


def test_delete_project_nlu_should_construct_request():
    transport, api = fixture_api()
    record_true(transport)
    api.delete_project_nlu(1, 'apiai')

    called = transport.called[0]
    assert called == (
        'delete',
        ('/projects/1/nlus/apiai', ),
        {
            'headers': {'Authorization': 'Bearer testtoken'}
        }
    )


def test_get_project_execution_logs_should_construct_request():
    transport, api = fixture_api()
    record_true(transport)
    response = api.get_project_execution_logs(1)
    assert response is True

    called = transport.called[0]
    assert called == (
        'get',
        ('/projects/1/logs', ),
        {
            'headers': {'Authorization': 'Bearer testtoken'}
        }
    )
