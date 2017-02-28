# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
import tarfile

from bothub_cli.api import Api
from bothub_cli.config import Config
from bothub_cli.config import ProjectConfig
from bothub_cli.utils import safe_mkdir
from bothub_cli.utils import write_content_to_file
from bothub_cli.utils import read_content_from_file
from bothub_cli.template import code as bot_code


API = Api()
CONFIG = Config()
PROJECT_CONFIG = ProjectConfig()


def create_py_project_structure():
    safe_mkdir('bothub')
    safe_mkdir('tests')
    write_content_to_file(os.path.join('bothub', '__init__.py'), '')
    write_content_to_file(os.path.join('bothub', 'bot.py'), bot_code)
    write_content_to_file('requirements.txt', '')


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


def init(name, project_config=None, api=None, config=None):
    _api = api or API
    _config = config or CONFIG
    _project_config = project_config or PROJECT_CONFIG
    _config.load()
    _api.load_auth(_config)
    project = _api.create_project(name)
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
        dependency = read_content_from_file('requirements.txt') or ''

        _api.upload_code(
            _project_config.get('id'),
            _project_config.get('programming-language'),
            dist_file,
            dependency
        )


def ls(api=None, config=None):
    _api = api or API
    _config = config or CONFIG
    _config.load()
    _api.load_auth(_config)
    return _api.list_projects()


def rm(name, api=None, config=None):
    _api = api or API
    _config = config or CONFIG
    _config.load()
    _api.load_auth(_config)
    projects = _api.list_projects()
    _projects = [p for p in projects if p['name'] == name]
    for project in _projects:
        _api.delete_project(project['id'])


def add_channel(channel, api_key, api=None, config=None, project_config=None):
    _api = api or API
    _config = config or CONFIG
    _project_config = project_config or PROJECT_CONFIG
    _config.load()
    _project_config.load()
    _api.load_auth(_config)
    _api.add_project_channel(_project_config.get('id'), channel, api_key)


def ls_channel(api=None, config=None, project_config=None):
    _api = api or API
    _config = config or CONFIG
    _project_config = project_config or PROJECT_CONFIG
    _config.load()
    _project_config.load()
    _api.load_auth(_config)
    channels = _api.get_project_channels(_project_config.get('id'))
    return [c['channel'] for c in channels]


def rm_channel(channel, api=None, config=None, project_config=None):
    _api = api or API
    _config = config or CONFIG
    _project_config = project_config or PROJECT_CONFIG
    _config.load()
    _project_config.load()
    _api.load_auth(_config)
    _api.delete_project_channels(_project_config.get('id'), channel)
