# -*- coding: utf-8 -*-

import requests_mock

from bothub_cli.clients import ExternalHttpStorageClient


def test_get_headers_should_returns_header_dict():
    client = ExternalHttpStorageClient('mytoken', 1)
    assert client.get_headers() == {
        'Authorization': 'Bearer mytoken',
        'Content-Type': 'application/json'
    }


def test_set_project_data_should_construct_request():
    with requests_mock.mock() as m:
        m.post('https://api.bothub.studio/api/projects/1/properties', text='{"data": true}')
        client = ExternalHttpStorageClient('mytoken', 1)
        assert client.set_project_data({'key': 'value'}) is True


def test_get_project_data_should_construct_request():
    with requests_mock.mock() as m:
        m.get('https://api.bothub.studio/api/projects/1/properties', text='{"data": true}')
        client = ExternalHttpStorageClient('mytoken', 1)
        assert client.get_project_data() is True
        

def test_set_user_data_should_construct_request():
    with requests_mock.mock() as m:
        m.post('https://api.bothub.studio/api/projects/1/user-properties/channels/mychannel/users/12345', text='{"data": true}')
        client = ExternalHttpStorageClient('mytoken', 1)
        assert client.set_user_data('mychannel', '12345', {'mytoken': 'value'}) is True
        

def test_get_user_data_should_construct_request():
    with requests_mock.mock() as m:
        m.get('https://api.bothub.studio/api/projects/1/user-properties/channels/mychannel/users/12345', text='{"data": true}')
        client = ExternalHttpStorageClient('mytoken', 1)
        assert client.get_user_data('mychannel', '12345') is True


def test_set_current_user_data_should_construct_request():
    with requests_mock.mock() as m:
        m.post('https://api.bothub.studio/api/projects/1/user-properties/channels/console/users/1', text='{"data": true}')
        client = ExternalHttpStorageClient('mytoken', 1)
        assert client.set_current_user_data({'mykey': 'myval'}) is True


def test_get_current_user_data_should_construct_request():
    with requests_mock.mock() as m:
        m.get('https://api.bothub.studio/api/projects/1/user-properties/channels/console/users/1', text='{"data": true}')
        client = ExternalHttpStorageClient('mytoken', 1)
        assert client.get_current_user_data() is True
        
