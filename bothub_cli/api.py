# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
import requests
from bothub_cli import exceptions as exc


BASE_URL = os.environ.get('BOTHUB_API_BASE_URL', 'https://api.bothub.studio/api')


class Api(object):
    def __init__(self, base_url=None, transport=None, auth_token=None):
        self.base_url = base_url or BASE_URL
        self.transport = transport or requests
        self.auth_token = auth_token

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

        if response.status_code == 404:
            raise exc.NotFound(self.get_response_cause(response))

        if response.status_code == 401:
            raise exc.InvalidCredential(self.get_response_cause(response))

        raise exc.CliException(self.get_response_cause(response))

    def authenticate(self, username, password):
        url = self.gen_url('users', 'access-token')
        data = {'username': username, 'password': password}
        response = self.transport.post(url, data)

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

    def create_project(self, name):
        url = self.gen_url('projects')
        data = {'name': name, 'short_name': name}
        headers = self.get_auth_headers()
        response = self.transport.post(url, json=data, headers=headers)
        self.check_response(response)
        return response.json()['data']

    def upload_code(self, project_id, language, code, dependency):
        url = self.gen_url('projects', project_id, 'bot')
        data = {'language': language, 'dependency': dependency}
        files = {'code': code}
        headers = self.get_auth_headers()
        response = self.transport.post(url, data=data, files=files, headers=headers)
        self.check_response(response)
        return response.json()['data']

    def list_projects(self):
        url = self.gen_url('users', 'self', 'projects')
        headers = self.get_auth_headers()
        response = self.transport.get(url, headers=headers)
        self.check_response(response)
        return response.json()['data']

    def delete_project(self, project_id):
        url = self.gen_url('projects', project_id)
        headers = self.get_auth_headers()
        response = self.transport.delete(url, headers=headers)
        self.check_response(response)

    def add_project_channel(self, project_id, channel, credentials):
        url = self.gen_url('projects', project_id, 'channels', channel)
        data = {'credentials': credentials}
        headers = self.get_auth_headers()
        response = self.transport.post(url, json=data, headers=headers)
        self.check_response(response)
        return response.json()['data']

    def get_project_channels(self, project_id):
        url = self.gen_url('projects', project_id, 'channels')
        headers = self.get_auth_headers()
        response = self.transport.get(url, headers=headers)
        self.check_response(response)
        return response.json()['data']

    def delete_project_channels(self, project_id, channel):
        url = self.gen_url('projects', project_id, 'channels', channel)
        headers = self.get_auth_headers()
        response = self.transport.delete(url, headers=headers)
        self.check_response(response)

    def set_project_property(self, project_id, key, value):
        url = self.gen_url('projects', project_id, 'properties')
        headers = self.get_auth_headers()
        data = {key: value}
        response = self.transport.post(url, json={'data': data}, headers=headers)
        self.check_response(response)
        return response.json()['data']

    def get_project_property(self, project_id):
        url = self.gen_url('projects', project_id, 'properties')
        headers = self.get_auth_headers()
        response = self.transport.get(url, headers=headers)
        self.check_response(response)
        return response.json()['data']
