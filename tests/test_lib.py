# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
import shutil

from bothub_cli import lib
from bothub_cli.api import Api
from bothub_cli.config import Config
from bothub_cli.config import ProjectConfig

from .testutils import MockResponse
from .testutils import MockTransport


def record_auth_token(transport):
    data = {'data': {'access_token': 'testtoken'}}
    response = MockResponse(data)
    transport.record(response)


def record_project(transport):
    data = {'data': {'id': 3, 'name': 'testproject', 'short_name': 'testproject'}}
    response = MockResponse(data)
    transport.record(response)


def record_upload_code(transport):
    data = {'data': {}}
    response = MockResponse(data)
    transport.record(response)


def fixture_api():
    transport = MockTransport()
    api = Api(transport=transport)
    return transport, api


def fixture_config(path=None):
    if path:
        return Config(path)
    _path = os.path.join('test_result', 'test_lib_config.yml')
    if os.path.isfile(_path):
        os.remove(_path)
    config = Config(_path)
    return config


def fixture_project_config(path=None):
    if path:
        return ProjectConfig(path)
    _path = os.path.join('test_result', 'test_lib_project_config.yml')
    if os.path.isfile(_path):
        os.remove(_path)
    config = ProjectConfig(_path)
    return config
    

def test_authenticate_should_save_config_file():
    transport, api = fixture_api()
    record_auth_token(transport)
    config = fixture_config()
    lib_cli = lib.Cli(config=config, api=api)
    lib_cli.authenticate('testuser', 'testpw')
    assert config.get('auth_token') == 'testtoken'


def test_init_should_save_config_file():
    transport, api = fixture_api()
    record_project(transport)
    record_upload_code(transport)
    config = fixture_config()
    config.set('auth_token', 'testtoken')
    config.save()
    shutil.copyfile(
        os.path.join('fixtures', 'test_bothub.yml'),
        os.path.join('test_result', 'test_lib_project_config.yml')
    )
    project_config = fixture_project_config()
    lib_cli = lib.Cli(project_config=project_config, api=api, config=config)
    lib_cli.init('testproject', '')
    assert project_config.get('id') == 3
    assert project_config.get('name') == 'testproject'
    with open(project_config.path) as fin:
        content = fin.read()
        assert 'testproject' in content
        assert '3' in content
