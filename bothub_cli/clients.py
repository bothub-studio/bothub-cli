# -*- coding: utf-8 -*-

import requests


class ConsoleChannelClient(object):
    def send_message(self, chat_id, message, channel=None, event=None, extra=None):
        _channel = '[{}] '.format(chat_id) if channel else ''
        _channel = '[{}:{}] '.format(channel, chat_id) if channel is not None else _channel
        print('{}{}'.format(_channel, message))


class ExternalHttpStorageClient(object):
    base_url = 'https://api.bothub.studio/api'

    def __init__(self, access_token, project_id, user=None):
        self.access_token = access_token
        self.project_id = project_id
        self.current_user = user or ('console', 1)

    def get_headers(self):
        return {
            'Authorization': 'Bearer {}'.format(self.access_token),
            'Content-Type': 'application/json'
        }

    def set_project_data(self, data):
        headers = self.get_headers()
        response = requests.post(
            '{}/projects/{}/properties'.format(self.base_url, self.project_id),
            json=data,
            headers=headers
        )
        return response.json()['data']

    def get_project_data(self):
        headers = self.get_headers()
        response = requests.get(
            '{}/projects/{}/properties'.format(self.base_url, self.project_id),
            headers=headers
        )
        return response.json()['data']

    def set_user_data(self, channel, user_id, data):
        headers = self.get_headers()
        response = requests.post(
            '{}/projects/{}/user-properties/channels/{}/users/{}'.format(
                self.base_url, self.project_id, channel, user_id
            ),
            headers=headers
        )
        return response.json()['data']

    def get_user_data(self, channel, user_id):
        headers = self.get_headers()
        response = requests.get(
            '{}/projects/{}/user-properties/channels/{}/users/{}'.format(
                self.base_url, self.project_id, channel, user_id
            ),
            headers=headers
        )
        return response.json()['data']

    def set_current_user_data(self, data):
        channel, user_id = self.current_user
        self.set_user_data(channel, user_id, data)

    def get_current_user_data(self):
        channel, user_id = self.current_user
        return self.get_user_data(channel, user_id)
