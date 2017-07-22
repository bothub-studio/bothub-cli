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
from .testutils import MockApi


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


def record_api_projects(api):
    api.responses.append([
        {'name': 'myfirstbot', 'status': 'online', 'regdate': '0000-00-00 00:00:00'},
        {'name': 'mysecondbot', 'status': 'online', 'regdate': '0000-00-00 00:00:00'},
    ])


def fixture_api():
    transport = MockTransport()
    api = Api(transport=transport, verify_token_expire=False)
    return transport, api


def fixture_config(path=None):
    if path:
        return Config(path)
    _path = os.path.join('test_result', 'test_lib_config.yml')
    if os.path.isfile(_path):
        os.remove(_path)
    config = Config(_path)
    config.set('auth_token', 'testtoken')
    config.save()
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
    cli = lib.Cli(config=config, api=api)
    cli.authenticate('testuser', 'testpw')
    assert config.get('auth_token') == 'testtoken'


def test_init_should_save_project_config_file():
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
    cli = lib.Cli(project_config=project_config, api=api, config=config)
    cli.init('testproject', '')
    assert project_config.get('id') == 3
    assert project_config.get('name') == 'testproject'
    with open(project_config.path) as fin:
        content = fin.read()
        assert 'testproject' in content
        assert '3' in content


def test_get_project_should_execute_api_get_project():
    api = MockApi()
    config = fixture_config()
    project_config = fixture_project_config()

    api.responses.append(True)

    cli = lib.Cli(project_config=project_config, api=api, config=config)
    assert cli.get_project(1) is True
    executed = api.executed.pop()
    assert executed == ('get_project', 1)


def test_ls_should_return_project_list():
    api = MockApi()
    config = fixture_config()
    project_config = fixture_project_config()

    record_api_projects(api)

    cli = lib.Cli(project_config=project_config, api=api, config=config)
    projects = cli.ls()
    executed = api.executed.pop()
    assert executed == ('list_project', )
    assert projects == [
        ['myfirstbot'],
        ['mysecondbot'],
    ]


def test_ls_should_return_project_list_detail():
    api = MockApi()
    config = fixture_config()
    project_config = fixture_project_config()

    record_api_projects(api)

    cli = lib.Cli(project_config=project_config, api=api, config=config)
    projects = cli.ls(verbose=True)
    executed = api.executed.pop()
    assert executed == ('list_project', )
    assert len(projects) == 2
    assert projects == [
        ['myfirstbot', 'online', '0000-00-00 00:00:00'],
        ['mysecondbot', 'online', '0000-00-00 00:00:00'],
    ]
