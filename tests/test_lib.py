# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
import shutil

import pytest

from bothub_cli import lib
from bothub_cli import exceptions as exc
from bothub_cli.api import Api
from bothub_cli.config import Config
from bothub_cli.config import ProjectConfig
from bothub_cli.utils import make_dist_package

from .testutils import MockResponse
from .testutils import MockTransport
from .testutils import MockApi


def teardown_function():
    shutil.rmtree('test_result', ignore_errors=True)


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
        {'id': 10, 'name': 'myfirstbot', 'status': 'online', 'regdate': '0000-00-00 00:00:00'},
        {'id': 20, 'name': 'mysecondbot', 'status': 'online', 'regdate': '0000-00-00 00:00:00'},
    ])


def record_api_channels(api):
    api.responses.append([
        {'id': 1, 'channel': 'myfirstchannel', 'credentials': {'api-key': 'myfirstkey'}},
        {'id': 2, 'channel': 'mychannel', 'credentials': {'api-key': 'myhiddenkey'}},
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


def test_rm_shoud_execute_delete_api():
    api = MockApi()
    config = fixture_config()
    project_config = fixture_project_config()

    record_api_projects(api)
    api.responses.append(True)

    cli = lib.Cli(project_config=project_config, api=api, config=config)
    cli.rm('myfirstbot')
    executed = api.executed.pop(0)
    assert executed == ('list_project', )
    executed2 = api.executed.pop(0)
    assert executed2 == ('delete_project', 10)


def test_rm_shoud_raise_not_found():
    api = MockApi()
    config = fixture_config()
    project_config = fixture_project_config()

    record_api_projects(api)
    api.responses.append(True)

    cli = lib.Cli(project_config=project_config, api=api, config=config)

    with pytest.raises(exc.ProjectNameNotFound):
        cli.rm('myfourthbot')
        executed = api.executed.pop(0)
        assert executed == ('list_project', )


def test_deploy_should_execute_upload_api():
    api = MockApi()
    config = fixture_config()
    project_config = fixture_project_config()
    shutil.copyfile(
        os.path.join('fixtures', 'test_bothub.yml'),
        os.path.join('test_result', 'test_lib_project_config.yml')
    )

    api.responses.append(True)
    api.responses.append({
        'id': 3,
        'name': 'WeatherBot',
        'status': 'online',
        'regdate': '0000-00-00 00:00:00'
    })

    source_dir = os.path.join('fixtures', 'code')
    cli = lib.Cli(project_config=project_config, api=api, config=config)
    cli.deploy(source_dir=source_dir)

    tar_path = os.path.join('test_result', 'bot.tgz')
    make_dist_package(tar_path, source_dir=source_dir)
    with open(tar_path, 'rb') as fin:
        tar_content = fin.read()

    executed = api.executed.pop(0)
    assert executed == ('upload_code', 3, 'python3', tar_content, 'bothub')


def test_clone_should_extract_code():
    api = MockApi()
    config = fixture_config()
    project_config = fixture_project_config()
    shutil.copyfile(
        os.path.join('fixtures', 'test_bothub.yml'),
        os.path.join('test_result', 'test_lib_project_config.yml')
    )
    api.responses.append([{
        'id': 3,
        'name': 'WeatherBot',
        'status': 'online',
        'regdate': '0000-00-00 00:00:00'
    }])
    with open(os.path.join('fixtures', 'bot.tgz'), 'rb') as fin:
        code = fin.read()
    api.responses.append({
        'code': str(code)
    })

    target_dir = os.path.join('test_result', 'clone_result')
    cli = lib.Cli(project_config=project_config, api=api, config=config)
    cli.clone('WeatherBot', target_dir)

    assert os.path.isdir(os.path.join('test_result', 'clone_result')) is True
    assert os.path.isdir(os.path.join('test_result', 'clone_result', 'code')) is True
    assert os.path.isfile(os.path.join('test_result', 'clone_result', 'code', 'sourcefile.txt')) is True


def test_add_channel_should_execute_api_call():
    api = MockApi()
    config = fixture_config()
    project_config = fixture_project_config()
    shutil.copyfile(
        os.path.join('fixtures', 'test_bothub.yml'),
        os.path.join('test_result', 'test_lib_project_config.yml')
    )
    api.responses.append(True)
    cli = lib.Cli(project_config=project_config, api=api, config=config)
    cli.add_channel('mychannel', {'api-key': 'mykey'})

    executed = api.executed.pop(0)
    assert executed == ('add_project_channel', 3, 'mychannel', {'api-key': 'mykey'})


def test_ls_channel_should_execute_api_call():
    api = MockApi()
    config = fixture_config()
    project_config = fixture_project_config()
    shutil.copyfile(
        os.path.join('fixtures', 'test_bothub.yml'),
        os.path.join('test_result', 'test_lib_project_config.yml')
    )
    record_api_channels(api)
    cli = lib.Cli(project_config=project_config, api=api, config=config)
    cli.ls_channel()

    executed = api.executed.pop(0)
    assert executed == ('get_project_channels', 3)


def test_rm_channel_should_execute_api_call():
    api = MockApi()
    config = fixture_config()
    project_config = fixture_project_config()
    shutil.copyfile(
        os.path.join('fixtures', 'test_bothub.yml'),
        os.path.join('test_result', 'test_lib_project_config.yml')
    )
    api.responses.append(True)
    cli = lib.Cli(project_config=project_config, api=api, config=config)
    cli.rm_channel('mychannel')

    executed = api.executed.pop(0)
    assert executed == ('delete_project_channel', 3, 'mychannel')


def test_ls_properties_should_execute_api_call():
    api = MockApi()
    config = fixture_config()
    project_config = fixture_project_config()
    shutil.copyfile(
        os.path.join('fixtures', 'test_bothub.yml'),
        os.path.join('test_result', 'test_lib_project_config.yml')
    )
    api.responses.append({
        'mykey': 'testval',
        'score': 100
    })
    cli = lib.Cli(project_config=project_config, api=api, config=config)
    cli.ls_properties()

    executed = api.executed.pop(0)
    assert executed == ('get_project_property', 3)


def test_set_properties_should_execute_api_call():
    api = MockApi()
    config = fixture_config()
    project_config = fixture_project_config()
    shutil.copyfile(
        os.path.join('fixtures', 'test_bothub.yml'),
        os.path.join('test_result', 'test_lib_project_config.yml')
    )
    api.responses.append(True)
    cli = lib.Cli(project_config=project_config, api=api, config=config)
    cli.set_properties('mykey', 'testval')

    executed = api.executed.pop(0)
    assert executed == ('set_project_property', 3, 'mykey', 'testval')


def test_get_properties_should_execute_api_call():
    api = MockApi()
    config = fixture_config()
    project_config = fixture_project_config()
    shutil.copyfile(
        os.path.join('fixtures', 'test_bothub.yml'),
        os.path.join('test_result', 'test_lib_project_config.yml')
    )
    api.responses.append({
        'mykey': 'myval'
    })
    cli = lib.Cli(project_config=project_config, api=api, config=config)
    result = cli.get_properties('mykey')
    assert result == 'myval'

    executed = api.executed.pop(0)
    assert executed == ('get_project_property', 3)


def test_rm_properties_should_execute_api_call():
    api = MockApi()
    config = fixture_config()
    project_config = fixture_project_config()
    shutil.copyfile(
        os.path.join('fixtures', 'test_bothub.yml'),
        os.path.join('test_result', 'test_lib_project_config.yml')
    )
    api.responses.append(True)
    cli = lib.Cli(project_config=project_config, api=api, config=config)
    cli.rm_properties('mykey')

    executed = api.executed.pop(0)
    assert executed == ('delete_project_property', 3, 'mykey')


def test_add_nlu_should_execute_api_call():
    api = MockApi()
    config = fixture_config()
    project_config = fixture_project_config()
    shutil.copyfile(
        os.path.join('fixtures', 'test_bothub.yml'),
        os.path.join('test_result', 'test_lib_project_config.yml')
    )
    api.responses.append(True)
    cli = lib.Cli(project_config=project_config, api=api, config=config)
    cli.add_nlu('mynlu', {'api-key': 'mykey'})

    executed = api.executed.pop(0)
    assert executed == ('add_project_nlu', 3, 'mynlu', {'api-key': 'mykey'})
    

def test_ls_nlus_should_execute_api_call():
    api = MockApi()
    config = fixture_config()
    project_config = fixture_project_config()
    shutil.copyfile(
        os.path.join('fixtures', 'test_bothub.yml'),
        os.path.join('test_result', 'test_lib_project_config.yml')
    )
    api.responses.append([
        {'nlu': 'apiai', 'credentials': {'api-key': 'testkey'}},
        {'nlu': 'witai', 'credentials': {'api-key': 'mytestkey'}},
    ])
    cli = lib.Cli(project_config=project_config, api=api, config=config)
    result = cli.ls_nlus()
    assert result == [
        ['apiai'],
        ['witai'],
    ]

    executed = api.executed.pop(0)
    assert executed == ('get_project_nlus', 3)


def test_ls_nlus_should_execute_api_call_and_list_detail():
    api = MockApi()
    config = fixture_config()
    project_config = fixture_project_config()
    shutil.copyfile(
        os.path.join('fixtures', 'test_bothub.yml'),
        os.path.join('test_result', 'test_lib_project_config.yml')
    )
    api.responses.append([
        {'nlu': 'apiai', 'credentials': {'api-key': 'testkey'}},
        {'nlu': 'witai', 'credentials': {'api-key': 'mytestkey'}},
    ])
    cli = lib.Cli(project_config=project_config, api=api, config=config)
    result = cli.ls_nlus(verbose=True)
    assert result == [
        ['apiai', {'api-key': 'testkey'}],
        ['witai', {'api-key': 'mytestkey'}],
    ]

    executed = api.executed.pop(0)
    assert executed == ('get_project_nlus', 3)


def test_rm_nlu_should_execute_api_call():
    api = MockApi()
    config = fixture_config()
    project_config = fixture_project_config()
    shutil.copyfile(
        os.path.join('fixtures', 'test_bothub.yml'),
        os.path.join('test_result', 'test_lib_project_config.yml')
    )
    api.responses.append(True)
    cli = lib.Cli(project_config=project_config, api=api, config=config)
    cli.rm_nlu('mynlu')

    executed = api.executed.pop(0)
    assert executed == ('delete_project_nlu', 3, 'mynlu')
