# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
import codecs
import shutil
from bothub_cli.config import ConfigBase
from bothub_cli.config import ProjectMeta


def setup_function():
    if not os.path.isdir('test_result'):
        os.makedirs('test_result')


def teardown_function():
    if os.path.isdir('test_result'):
        shutil.rmtree('test_result')


def fixture_config(filename='test.yml'):
    shutil.rmtree('test_result', ignore_errors=True)
    config = ConfigBase(os.path.join('test_result', filename))
    return config


def test_config_save_should_make_file():
    config = fixture_config()
    config.save()
    assert os.path.isfile(os.path.join('test_result', 'test.yml'))


def test_config_set_should_create_entry():
    config = fixture_config()
    config.set('auth_token', 'testtoken')
    config.save()
    assert os.path.isfile(os.path.join('test_result', 'test.yml'))
    with open(os.path.join('test_result', 'test.yml')) as fin:
        content = fin.read()
        assert 'testtoken' in content


def test_config_setitem_should_create_entry():
    config = fixture_config()
    config['auth_token'] = 'testtoken'
    config.save()
    assert os.path.isfile(os.path.join('test_result', 'test.yml'))
    with open(os.path.join('test_result', 'test.yml')) as fin:
        content = fin.read()
        assert 'testtoken' in content


def test_config_contains_should_true():
    config = fixture_config()
    config['auth_token'] = 'testtoken'
    assert 'auth_token' in config


def test_config_load_and_get_should_contains_entry():
    config = fixture_config('test2.yml')
    config.save()

    with codecs.open(os.path.join('test_result', 'test2.yml'), 'wb', encoding='utf8') as fout:
        content = 'auth_token: testtoken'
        fout.write(content)

    config.load()
    assert config.get('auth_token') == 'testtoken'


def test_config_load_and_getitem_should_contains_entry():
    config = fixture_config('test2.yml')
    config.save()

    with codecs.open(os.path.join('test_result', 'test2.yml'), 'wb', encoding='utf8') as fout:
        content = 'auth_token: testtoken'
        fout.write(content)

    config.load()
    assert config['auth_token'] == 'testtoken'


def test_config_del_should_remove_entry():
    config = fixture_config('test2.yml')
    config.save()

    with codecs.open(os.path.join('test_result', 'test2.yml'), 'wb', encoding='utf8') as fout:
        content = 'auth_token: testtoken'
        fout.write(content)

    config.load()
    assert config['auth_token'] == 'testtoken'
    assert 'auth_token' in config
    del config['auth_token']
    assert 'auth_token' not in config


def test_migrate_should_move_some_entries():
    project_meta_path = os.path.join('test_result', 'test_lib_project_meta.yml')
    project_meta = ProjectMeta(project_meta_path)

    project_config_path = os.path.join('test_result', 'test_lib_dummy_config.yml')
    project_config = ConfigBase(project_config_path)
    project_config['id'] = 30
    project_config['name'] = 'testproject'

    project_meta.migrate_from_project_config(project_config)

    assert project_meta['id'] == 30
    assert project_meta['name'] == 'testproject'
    
    assert 'id' not in project_config
    assert 'name' not in project_config
