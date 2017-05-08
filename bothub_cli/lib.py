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
from bothub_cli.utils import write_content_to_file
from bothub_cli.utils import read_content_from_file
from bothub_cli.template import code as bot_code


API = Api()
CONFIG = Config()
PROJECT_CONFIG = ProjectConfig()


def get_project_id(project_config):
    project_id = project_config.get('id')
    if not project_id:
        raise exc.ImproperlyConfigured("Invalid project directory. Did you run 'bothub init' for current directory before?")

    return project_id


def create_py_project_structure():
    safe_mkdir('bothub')
    safe_mkdir('tests')
    write_content_to_file(os.path.join('bothub', '__init__.py'), '')
    write_content_to_file(os.path.join('bothub', 'bot.py'), bot_code)
    write_content_to_file('requirements.txt', 'bothub')


PROJECT_STRUCTURE_HANDLERS = {
    'python3': create_py_project_structure,
    'python': create_py_project_structure,
}


def authenticate(username, password, api=None, config=None):
    _api = api or API
    _config = config or CONFIG
    token = _api.authenticate(username, password)
    _config.set('auth_token', token)
    _config.save()


def init(name, description, project_config=None, api=None, config=None):
    _api = api or API
    _config = config or CONFIG
    _project_config = project_config or PROJECT_CONFIG
    _config.load()
    _api.load_auth(_config)
    project = _api.create_project(name, description)
    project_id = project['id']
    project_name = project['name']
    programming_language = 'python3'
    _project_config.set('id', project_id)
    _project_config.set('name', project_name)
    _project_config.set('programming-language', programming_language)
    _project_config.save()
    PROJECT_STRUCTURE_HANDLERS[programming_language]()


def make_dist_package(dist_file_path):
    if os.path.isfile(dist_file_path):
        os.remove(dist_file_path)

    with tarfile.open(dist_file_path, 'w:gz') as tout:
        for fname in os.listdir('.'):
            if os.path.isfile(fname):
                tout.add(fname)
            elif os.path.isdir(fname) and fname in ['bothub', 'tests']:
                tout.add(fname)


def deploy(project_config=None, api=None, config=None):
    _api = api or API
    _config = config or CONFIG
    _project_config = project_config or PROJECT_CONFIG
    _config.load()
    _project_config.load()
    _api.load_auth(_config)

    safe_mkdir('dist')
    dist_file_path = os.path.join('dist', 'bot.tgz')
    make_dist_package(dist_file_path)

    with open(dist_file_path, 'rb') as dist_file:
        dependency = read_content_from_file('requirements.txt') or 'bothub'
        project_id = get_project_id(_project_config)
        _api.upload_code(
            project_id,
            _project_config.get('programming-language'),
            dist_file,
            dependency
        )


def ls(api=None, config=None):
    _api = api or API
    _config = config or CONFIG
    _config.load()
    _api.load_auth(_config)
    return [[p['name']] for p in _api.list_projects()]


def rm(name, api=None, config=None):
    _api = api or API
    _config = config or CONFIG
    _config.load()
    _api.load_auth(_config)
    projects = _api.list_projects()
    _projects = [p for p in projects if p['name'] == name]
    if not _projects:
        raise exc.NotFound('No such project: {}'.format(name))
    for project in _projects:
        _api.delete_project(project['id'])


def add_channel(channel, credentials, api=None, config=None, project_config=None):
    _api = api or API
    _config = config or CONFIG
    _project_config = project_config or PROJECT_CONFIG
    _config.load()
    _project_config.load()
    _api.load_auth(_config)
    project_id = get_project_id(_project_config)
    _api.add_project_channel(project_id, channel, credentials)


def ls_channel(verbose=False, api=None, config=None, project_config=None):
    _api = api or API
    _config = config or CONFIG
    _project_config = project_config or PROJECT_CONFIG
    _config.load()
    _project_config.load()
    _api.load_auth(_config)
    project_id = get_project_id(_project_config)
    channels = _api.get_project_channels(project_id)
    if verbose:
        result = [[c['channel'], c['credentials']] for c in channels]
    else:
        result = [[c['channel']] for c in channels]
    return result


def rm_channel(channel, api=None, config=None, project_config=None):
    _api = api or API
    _config = config or CONFIG
    _project_config = project_config or PROJECT_CONFIG
    _config.load()
    _project_config.load()
    _api.load_auth(_config)
    project_id = get_project_id(_project_config)
    _api.delete_project_channels(project_id, channel)


def ls_properties(api=None, config=None, project_config=None):
    _api = api or API
    _config = config or CONFIG
    _project_config = project_config or PROJECT_CONFIG
    _config.load()
    _project_config.load()
    _api.load_auth(_config)
    project_id = get_project_id(_project_config)
    return _api.get_project_property(project_id)


def get_properties(key, api=None, config=None, project_config=None):
    _api = api or API
    _config = config or CONFIG
    _project_config = project_config or PROJECT_CONFIG
    _config.load()
    _project_config.load()
    _api.load_auth(_config)
    project_id = get_project_id(_project_config)
    data = _api.get_project_property(project_id)
    return data.get(key)


def set_properties(key, value, api=None, config=None, project_config=None):
    try:
        _value = json.loads(value)
    except ValueError:
        raise exc.InvalidValue('Not proper JSON type: {}'.format(value))

    _api = api or API
    _config = config or CONFIG
    _project_config = project_config or PROJECT_CONFIG
    _config.load()
    _project_config.load()
    _api.load_auth(_config)
    project_id = get_project_id(_project_config)
    return _api.set_project_property(project_id, key, _value)


def rm_properties(key, api=None, config=None, project_config=None):
    _api = api or API
    _config = config or CONFIG
    _project_config = project_config or PROJECT_CONFIG
    _config.load()
    _project_config.load()
    _api.load_auth(_config)
    project_id = get_project_id(_project_config)
    _api.delete_project_property(project_id, key)


def print_cursor():
    print('BotHub>', end=' ', flush=True)


def make_event(message):
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


def test(config=None, project_config=None):
    _config = config or CONFIG
    _project_config = project_config or PROJECT_CONFIG
    _config.load()
    _project_config.load()

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
