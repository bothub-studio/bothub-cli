# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
import time
import logging
from datetime import datetime

import requests
import jwt
from bothub_cli import exceptions as exc
from bothub_cli.utils import timestamp


logger = logging.getLogger('bothub.cli.api')


class ApiBase(object):
    def __init__(self, base_url=None, transport=None, auth_token=None, verify_token_expire=True):
        env_base_url = os.environ.get('BOTHUB_API_BASE_URL',
                                      'https://api.bothub.studio/api')
        self.base_url = base_url if base_url is not None else env_base_url
        self.transport = transport or requests
        self.auth_token = auth_token
        self.verify_token_expire = verify_token_expire

    def _send_request(self, *args, **kwargs):
        method = kwargs.pop('method', 'get')
        func = getattr(self.transport, method)
        result = func(*args, **kwargs)
        return result

    def _check_auth_token_expired(self):
        logger.debug('Check auth token expiraration')
        if not self.verify_token_expire:
            logger.debug('Skip token expiraration check on debug mode')
            return

        content = jwt.decode(self.auth_token, verify=False)
        now_timestamp = timestamp()
        if now_timestamp > content['exp']:
            logger.debug('Token is expired: exp[%s] < now[%s]', content['exp'], now_timestamp)
            raise exc.AuthTokenExpired()

    def _gen_url(self, *args):
        return '{}/{}'.format(self.base_url, '/'.join([str(arg) for arg in args]))

    def _get_response_cause(self, response):
        if response.json() == '':
            return
        return response.json().get('cause')

    def _check_auth_token(self):
        if not self.auth_token:
            raise exc.NoCredential()

        self._check_auth_token_expired()

    def _check_response(self, response):
        if response.status_code // 100 in [2, 3]:
            return

        if response.status_code == 401:
            raise exc.InvalidCredential(
                "Authentication is failed. "\
                "Try 'bothub configure' to verify login credentials: {}"\
                .format(self._get_response_cause(response)))

        if response.status_code == 404:
            raise exc.NotFound('Resource not found: {}'\
                               .format(self._get_response_cause(response)))

        if response.status_code == 409:
            raise exc.Duplicated(self._get_response_cause(response))

        raise exc.CliException(self._get_response_cause(response))

    def _get_auth_headers(self):
        self._check_auth_token()
        headers = {'Authorization': 'Bearer {}'.format(self.auth_token)}
        return headers


class Api(ApiBase):
    '''Communicate with BotHub.Studio server'''

    def load_auth(self, config):
        self.auth_token = config.get('auth_token')

    def authenticate(self, username, password):
        url = self._gen_url('users', 'access-token')
        data = {'username': username, 'password': password}
        response = self._send_request(url, data, method='post')

        if response.status_code == 404:
            raise exc.UserNotFound(username)

        if response.status_code == 401:
            raise exc.AuthenticationFailed()

        self._check_response(response)
        response_dict = response.json()['data']
        return response_dict['access_token']

    def get_webhook_url(self, channel, project_id):
        url = self._gen_url('projects', project_id, 'webhooks', channel)
        return url

    def list_projects(self):
        url = self._gen_url('users', 'self', 'projects')
        headers = self._get_auth_headers()
        response = self._send_request(url, headers=headers)
        self._check_response(response)
        return response.json()['data']

    def create_project(self, name, description):
        try:
            url = self._gen_url('projects')
            data = {'name': name, 'short_name': name, 'description': description}
            headers = self._get_auth_headers()
            response = self._send_request(url, json=data, headers=headers, method='post')
            self._check_response(response)
            return response.json()['data']
        except exc.Duplicated:
            raise exc.ProjectNameDuplicated(name)

    def get_project(self, project_id):
        try:
            url = self._gen_url('projects', project_id)
            headers = self._get_auth_headers()
            response = self._send_request(url, headers=headers)
            self._check_response(response)
            return response.json()['data']
        except exc.NotFound:
            raise exc.ProjectIdNotFound(project_id)

    def delete_project(self, project_id):
        url = self._gen_url('projects', project_id)
        headers = self._get_auth_headers()
        response = self._send_request(url, headers=headers, method='delete')
        self._check_response(response)

    def add_project_channel(self, project_id, channel, credentials):
        url = self._gen_url('projects', project_id, 'channels', channel)
        data = {'credentials': credentials}
        headers = self._get_auth_headers()
        response = self._send_request(url, json=data, headers=headers, method='post')
        self._check_response(response)
        return response.json()['data']

    def get_project_channels(self, project_id):
        url = self._gen_url('projects', project_id, 'channels')
        headers = self._get_auth_headers()
        response = self._send_request(url, headers=headers, method='get')
        self._check_response(response)
        return response.json()['data']

    def delete_project_channels(self, project_id, channel):
        url = self._gen_url('projects', project_id, 'channels', channel)
        headers = self._get_auth_headers()
        response = self._send_request(url, headers=headers, method='delete')
        self._check_response(response)

    def upload_code(self, project_id, language, code=None, dependency=None):
        url = self._gen_url('projects', project_id, 'bot')
        data = {'language': language}
        if dependency:
            data['dependency'] = dependency
        files = {'code': code} if code else None
        headers = self._get_auth_headers()
        response = self._send_request(
            url, data=data, files=files, headers=headers, method='post'
        )
        self._check_response(response)
        return response.json()['data']

    def get_code(self, project_id):
        url = self._gen_url('projects', project_id, 'bot')
        headers = self._get_auth_headers()
        response = self._send_request(url, headers=headers, method='get')
        self._check_response(response)
        return response.json()['data']

    def set_project_property(self, project_id, key, value):
        url = self._gen_url('projects', project_id, 'properties')
        headers = self._get_auth_headers()
        data = {key: value}
        response = self._send_request(
            url, json={'data': data}, headers=headers, method='post'
        )
        self._check_response(response)
        return response.json()['data']

    def get_project_property(self, project_id):
        url = self._gen_url('projects', project_id, 'properties')
        headers = self._get_auth_headers()
        response = self._send_request(url, headers=headers, method='get')
        self._check_response(response)
        return response.json()['data']

    def delete_project_property(self, project_id, key):
        url = self._gen_url('projects', project_id, 'properties', key)
        headers = self._get_auth_headers()
        response = self._send_request(url, headers=headers, method='delete')
        self._check_response(response)

    def add_project_nlu(self, project_id, nlu, credentials):
        url = self._gen_url('projects', project_id, 'nlus')
        data = {'credentials': credentials, 'nlu': nlu}
        headers = self._get_auth_headers()
        response = self._send_request(url, json=data, headers=headers, method='post')
        self._check_response(response)
        return response.json()['data']

    def get_project_nlus(self, project_id):
        url = self._gen_url('projects', project_id, 'nlus')
        headers = self._get_auth_headers()
        response = self._send_request(url, headers=headers)
        self._check_response(response)
        return response.json()['data']

    def get_project_nlu(self, project_id, nlu):
        url = self._gen_url('projects', project_id, 'nlus', nlu)
        headers = self._get_auth_headers()
        response = self._send_request(url, headers=headers)
        self._check_response(response)
        return response.json()['data']

    def delete_project_nlu(self, project_id, nlu):
        url = self._gen_url('projects', project_id, 'nlus', nlu)
        headers = self._get_auth_headers()
        response = self._send_request(url, headers=headers, method='delete')
        self._check_response(response)

    def get_project_execution_logs(self, project_id):
        url = self._gen_url('projects', project_id, 'logs')
        headers = self._get_auth_headers()
        response = self._send_request(url, headers=headers)
        self._check_response(response)
        return response.json()['data']
