# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
import click
import requests
from bothub_cli import exceptions as exc


BASE_URL = os.environ.get('BOTHUB_API_BASE_URL', 'https://api.bothub.studio/api')


class Api(object):
    def __init__(self, base_url=None, transport=None, auth_token=None):
        self.base_url = base_url or BASE_URL
        self.transport = transport or requests
        self.auth_token = auth_token

    def send_request(self, *args, **kwargs):
        method = kwargs.pop('method', 'get')
        func = getattr(self.transport, method)
        result = func(*args, **kwargs)
        return result

    def load_auth(self, config):
        self.auth_token = config.get('auth_token')

    def gen_url(self, *args):
        return '{}/{}'.format(self.base_url, '/'.join([str(arg) for arg in args]))

    def get_response_cause(self, response):
        if response.json() == '':
            return
        return response.json().get('cause')

    def check_auth_token(self):
        if not self.auth_token:
            raise exc.NoCredential()

    def check_response(self, response):
        if response.status_code // 100 in [2, 3]:
            return

        if response.status_code == 401:
            raise exc.InvalidCredential("Authentication is failed. Try 'bothub configure' to login again: {}".format(self.get_response_cause(response)))

        if response.status_code == 404:
            raise exc.NotFound('Resource not found: {}'.format(self.get_response_cause(response)))

        if response.status_code == 409:
            raise exc.Duplicated(self.get_response_cause(response))

        raise exc.CliException(self.get_response_cause(response))

    def authenticate(self, username, password):
        url = self.gen_url('users', 'access-token')
        data = {'username': username, 'password': password}
        response = self.send_request(url, data, method='post')

        if response.status_code == 404:
            raise exc.NotFound('No such user {}'.format(username))

        if response.status_code == 401:
            raise exc.InvalidCredential('Invalid username/password')

        self.check_response(response)
        response_dict = response.json()['data']
        return response_dict['access_token']

    def get_auth_headers(self):
        self.check_auth_token()
        headers = {'Authorization': 'Bearer {}'.format(self.auth_token)}
        return headers

    def create_project(self, name, description):
        try:
            url = self.gen_url('projects')
            data = {'name': name, 'short_name': name, 'description': description}
            headers = self.get_auth_headers()
            response = self.send_request(url, json=data, headers=headers, method='post')
            self.check_response(response)
            return response.json()['data']
        except exc.Duplicated:
            raise exc.Duplicated('Project name already exists. Please use other name')

    def get_project(self, project_id):
        try:
            url = self.gen_url('projects', project_id)
            headers = self.get_auth_headers()
            response = self.send_request(url, headers=headers)
            self.check_response(response)
            return response.json()['data']
        except exc.NotFound:
            raise exc.NotFound('Project {} is not exists.'.format(project_id))

    def upload_code(self, project_id, language, code=None, dependency=None):
        url = self.gen_url('projects', project_id, 'bot')
        data = {'language': language}
        if dependency:
            data['dependency'] = dependency
        files = {'code': code} if code else None
        headers = self.get_auth_headers()
        response = self.send_request(url, data=data, files=files, headers=headers, method='post')
        self.check_response(response)
        return response.json()['data']

    def get_code(self, project_id):
        url = self.gen_url('projects', project_id, 'bot')
        headers = self.get_auth_headers()
        response = self.send_request(url, headers=headers, method='get')
        self.check_response(response)
        return response.json()['data']

    def list_projects(self):
        url = self.gen_url('users', 'self', 'projects')
        headers = self.get_auth_headers()
        response = self.send_request(url, headers=headers)
        self.check_response(response)
        return response.json()['data']

    def delete_project(self, project_id):
        url = self.gen_url('projects', project_id)
        headers = self.get_auth_headers()
        response = self.send_request(url, headers=headers, method='delete')
        self.check_response(response)

    def add_project_channel(self, project_id, channel, credentials):
        url = self.gen_url('projects', project_id, 'channels', channel)
        data = {'credentials': credentials}
        headers = self.get_auth_headers()
        response = self.send_request(url, json=data, headers=headers, method='post')
        self.check_response(response)
        return response.json()['data']

    def get_project_channels(self, project_id):
        url = self.gen_url('projects', project_id, 'channels')
        headers = self.get_auth_headers()
        response = self.send_request(url, headers=headers, method='get')
        self.check_response(response)
        return response.json()['data']

    def delete_project_channels(self, project_id, channel):
        url = self.gen_url('projects', project_id, 'channels', channel)
        headers = self.get_auth_headers()
        response = self.send_request(url, headers=headers, method='delete')
        self.check_response(response)

    def set_project_property(self, project_id, key, value):
        url = self.gen_url('projects', project_id, 'properties')
        headers = self.get_auth_headers()
        data = {key: value}
        response = self.send_request(url, json={'data': data}, headers=headers, method='post')
        self.check_response(response)
        return response.json()['data']

    def get_project_property(self, project_id):
        url = self.gen_url('projects', project_id, 'properties')
        headers = self.get_auth_headers()
        response = self.send_request(url, headers=headers, method='get')
        self.check_response(response)
        return response.json()['data']

    def delete_project_property(self, project_id, key):
        url = self.gen_url('projects', project_id, 'properties', key)
        headers = self.get_auth_headers()
        response = self.send_request(url, headers=headers, method='delete')
        self.check_response(response)

    def add_project_nlu(self, project_id, nlu, credentials):
        url = self.gen_url('projects', project_id, 'nlus')
        data = {'credentials': credentials, 'nlu': nlu}
        headers = self.get_auth_headers()
        response = self.send_request(url, json=data, headers=headers, method='post')
        self.check_response(response)
        return response.json()['data']

    def get_project_nlus(self, project_id):
        url = self.gen_url('projects', project_id, 'nlus')
        headers = self.get_auth_headers()
        response = self.send_request(url, headers=headers)
        self.check_response(response)
        return response.json()['data']

    def get_project_nlu(self, project_id, nlu):
        url = self.gen_url('projects', project_id, 'nlus', nlu)
        headers = self.get_auth_headers()
        response = self.send_request(url, headers=headers)
        self.check_response(response)
        return response.json()['data']

    def delete_project_nlu(self, project_id, nlu):
        url = self.gen_url('projects', project_id, 'nlus', nlu)
        headers = self.get_auth_headers()
        response = self.send_request(url, headers=headers, method='delete')
        self.check_response(response)

    def get_project_execution_logs(self, project_id):
        url = self.gen_url('projects', project_id, 'logs')
        headers = self.get_auth_headers()
        response = self.send_request(url, headers=headers)
        self.check_response(response)
        return response.json()['data']
