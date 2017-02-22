# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)

import os

from bothub_cli.api import Api
from bothub_cli.config import Config
from bothub_cli.config import ProjectConfig
from bothub_cli.utils import safe_mkdir
from bothub_cli.utils import write_content_to_file
from bothub_cli.utils import read_content_from_file


API = Api()
CONFIG = Config()
PROJECT_CONFIG = ProjectConfig()


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
    create_py_project_structure()


def create_py_project_structure():
    safe_mkdir('src')
    safe_mkdir('tests')
    write_content_to_file(os.path.join('src', 'bot.py'), '')
    write_content_to_file('requirements.txt', '')


def deploy(project_config=None, api=None, config=None):
    _api = api or API
    _config = config or CONFIG
    _project_config = project_config or PROJECT_CONFIG
    _config.load()
    _project_config.load()
    _api.load_auth(_config)

    dependency = read_content_from_file('requirements.txt') or ''
    code = read_content_from_file(os.path.join('src', 'bothub.py')) or ''

    _api.upload_code(
        _project_config.get('id'),
        _project_config.get('programming-language'),
        code,
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
