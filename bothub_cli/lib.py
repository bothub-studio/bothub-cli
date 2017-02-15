# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)

from bothub_cli.api import Api
from bothub_cli.config import Config
from bothub_cli.config import ProjectConfig


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


def package():
    return


def upload():
    return
