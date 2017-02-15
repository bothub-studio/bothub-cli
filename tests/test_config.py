# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
import codecs
import shutil
from bothub_cli.config import Config


def fixture_config(filename='test.yml'):
    shutil.rmtree('test_result')
    config = Config(os.path.join('test_result', filename))
    return config


def test_config_init_should_make_parent_dir():
    fixture_config()
    assert os.path.isdir('test_result')


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


def test_config_load_and_get_should_contains_entry():
    config = fixture_config('test2.yml')

    with codecs.open(os.path.join('test_result', 'test2.yml'), 'wb', encoding='utf8') as fout:
        content = 'auth_token: testtoken'
        fout.write(content)

    config.load()
    assert config.get('auth_token') == 'testtoken'
