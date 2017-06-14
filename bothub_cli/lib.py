# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
import sys
import json
import tarfile

from bothub_client.clients import ConsoleChannelClient
from bothub_client.clients import LocMemStorageClient

from bothub_cli.api import Api
from bothub_cli.config import Config
from bothub_cli.config import ProjectConfig
from bothub_cli import exceptions as exc
from bothub_cli.utils import safe_mkdir
from bothub_cli.utils import read_content_from_file


def make_dist_package(dist_file_path):
    '''Make dist package file of current project directory.
    Includes all files of current dir, bothub dir and tests dir.
    Dist file is compressed with tar+gzip.'''
    if os.path.isfile(dist_file_path):
        os.remove(dist_file_path)

    with tarfile.open(dist_file_path, 'w:gz') as tout:
        for fname in os.listdir('.'):
            if os.path.isfile(fname):
                tout.add(fname)
            elif os.path.isdir(fname) and fname in ['bothub', 'tests']:
                tout.add(fname)


def extract_dist_package(dist_file_path):
    '''Extract dist package file to current directory.'''
    with tarfile.open(dist_file_path, 'r:gz') as tin:
        tin.extractall()


def print_cursor():
    '''Print test mode cursor.'''
    print('BotHub>', end=' ', flush=True)


def make_event(message):
    '''Make dummy event for test mode.'''
    return {
        'trigger': 'cli',
        'channel': 'cli',
        'sender': {
            'id': 'localuser',
            'name': 'Local user'
        },
        'content': message,
        'raw_data': message
    }


class Cli(object):
    '''A CLI class represents '''
    def __init__(self, api=None, config=None, project_config=None):
        self.api = api or Api()
        self.config = config or Config()
        self.project_config = project_config or ProjectConfig()

    def load_auth(self):
        '''Load auth token from bothub config and inject to API class'''
        self.config.load()
        self.api.load_auth(self.config)

    def get_current_project_id(self):
        self.project_config.load()
        project_id = self.project_config.get('id')
        if not project_id:
            raise exc.ImproperlyConfigured("Invalid project directory. "
                                           "Did you run 'bothub init' for current directory before?")
        return project_id

    def get_project(self, project_id):
        self.load_auth()
        return self.api.get_project(project_id)

    def authenticate(self, username, password):
        token = self.api.authenticate(username, password)
        self.config.set('auth_token', token)
        self.config.save()

    def get_project_id_with_name(self, project_name):
        self.load_auth()
        projects = self.api.list_projects()
        for p in projects:
            if p['name'] == project_name:
                return p['id']
        raise exc.NotFound('Such project {} is not found'.format(project_name))

    def init(self, name, description):
        self.load_auth()
        project = self.api.create_project(name, description)
        project_id = project['id']
        programming_language = 'python3'
        self.api.upload_code(project_id, programming_language)

    def deploy(self):
        self.load_auth()
        self.project_config.load()

        safe_mkdir('dist')
        dist_file_path = os.path.join('dist', 'bot.tgz')
        make_dist_package(dist_file_path)

        with open(dist_file_path, 'rb') as dist_file:
            dependency = read_content_from_file('requirements.txt') or 'bothub'
            project_id = self.get_current_project_id()
            self.api.upload_code(
                project_id,
                self.project_config.get('programming-language'),
                dist_file,
                dependency
            )

    def clone(self, project_name):
        project_id = self.get_project_id_with_name(project_name)
        self.load_auth()

        response = self.api.get_code(project_id)
        code = response['code']
        code_byte = eval(code)

        with open('code.tgz', 'wb') as code_file:
            code_file.write(code_byte)

        extract_dist_package('code.tgz')
        if os.path.isfile('code.tgz'):
            os.remove('code.tgz')

    def ls(self):
        self.load_auth()
        return [[p['name']] for p in self.api.list_projects()]

    def rm(self, name):
        self.load_auth()
        projects = self.api.list_projects()
        _projects = [p for p in projects if p['name'] == name]
        if not _projects:
            raise exc.NotFound('No such project: {}'.format(name))
        for project in _projects:
            self.api.delete_project(project['id'])

    def add_channel(self, channel, credentials):
        self.load_auth()
        self.project_config.load()
        project_id = self.get_current_project_id()
        self.api.add_project_channel(project_id, channel, credentials)

    def ls_channel(self, verbose=False):
        self.load_auth()
        self.project_config.load()
        project_id = self.get_current_project_id()
        channels = self.api.get_project_channels(project_id)
        if verbose:
            result = [[c['channel'], c['credentials']] for c in channels]
        else:
            result = [[c['channel']] for c in channels]
        return result

    def rm_channel(self, channel):
        self.load_auth()
        self.project_config.load()
        project_id = self.get_current_project_id()
        self.api.delete_project_channels(project_id, channel)

    def ls_properties(self):
        self.load_auth()
        self.project_config.load()
        project_id = self.get_current_project_id()
        return self.api.get_project_property(project_id)

    def get_properties(self, key):
        self.load_auth()
        self.project_config.load()
        project_id = self.get_current_project_id()
        data = self.api.get_project_property(project_id)
        return data.get(key)

    def set_properties(self, key, value):
        try:
            _value = json.loads(value)
        except ValueError:
            raise exc.InvalidValue('Not proper JSON type: {}'.format(value))

        self.load_auth()
        self.project_config.load()
        project_id = self.get_current_project_id()
        return self.api.set_project_property(project_id, key, _value)

    def rm_properties(self, key):
        self.load_auth()
        self.project_config.load()
        project_id = self.get_current_project_id()
        self.api.delete_project_property(project_id, key)

    def test(self):
        self.load_auth()
        self.project_config.load()

        try:
            sys.path.append('.')
            __import__('bothub.bot')
        except ImportError:
            if sys.exc_info()[-1].tb_next:
                raise
            else:
                raise exc.ModuleLoadException('We found no valid bothub app on bothub/bot.py')

        mod = sys.modules['bothub.bot']
        channel_client = ConsoleChannelClient()
        storage_client = LocMemStorageClient()
        bot = mod.Bot(channel_client=channel_client, storage_client=storage_client)

        print_cursor()
        line = sys.stdin.readline()
        while line:
            try:
                event = make_event(line)
                context = {}
                bot.handle_message(event, context)
                print_cursor()
                line = sys.stdin.readline()
            except Exception as ex:
                print(ex)
                print_cursor()
                line = sys.stdin.readline()
        print('\n')

    def add_nlu(self, nlu, credentials):
        self.load_auth()
        self.project_config.load()
        project_id = self.get_current_project_id()
        self.api.add_project_nlu(project_id, nlu, credentials)

    def ls_nlus(self, verbose=False):
        self.load_auth()
        self.project_config.load()
        project_id = self.get_current_project_id()
        nlus = self.api.get_project_nlus(project_id)
        if verbose:
            result = [[nlu['nlu'], nlu['credentials']] for nlu in nlus]
        else:
            result = [[nlu['nlu']] for nlu in nlus]
        return result

    def rm_nlu(self, nlu):
        self.load_auth()
        self.project_config.load()
        project_id = self.get_current_project_id()
        self.api.delete_project_nlu(project_id, nlu)
