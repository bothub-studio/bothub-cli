# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)

import requests
from bothub_cli import exceptions as exc


BASE_URL = 'https://api.bothub.studio/api'


class Api(object):
    def __init__(self, base_url=None, transport=None):
        self.base_url = base_url or BASE_URL
        self.transport = transport or requests

    def gen_url(self, *args):
        return '{}/{}'.format(self.base_url, '/'.join(args))

    def authenticate(self, username, password):
        url = self.gen_url('users', 'access-token')
        data = {'username': username, 'password': password}
        response = self.transport.post(url, data)
        if response.status_code == '401':
            raise exc.InvalidCredential(response.json()['cause'])

        response_dict = response.json()
        return response_dict['access_token']
