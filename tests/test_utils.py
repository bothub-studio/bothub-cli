# -*- coding: utf-8 -*-

import os
import shutil
import requests_mock
import yaml

from datetime import datetime
from datetime import timedelta

from bothub_cli import utils


CACHE_DIR = os.path.join('test_result', 'cache')
CACHE_FILE_PATH = os.path.join('test_result', 'cache', 'test_cache.yml')


def setup_function():
    if os.path.isdir(CACHE_DIR):
        shutil.rmtree(CACHE_DIR)


# def teardown_function():
#     if os.path.isdir(CACHE_DIR):
#         shutil.rmtree(CACHE_DIR)


def fixture_cache_data():
    data = {
        'mykey': {
            'value': 'myvalue',
            'expires': datetime.now() + timedelta(seconds=60)
        }
    }
    return data


def test_cache_init_should_make_parent_dir():
    cache = utils.Cache(CACHE_FILE_PATH)
    assert os.path.isdir(CACHE_DIR) is True


def test_cache_get_should_return_none_with_no_cache_file():
    cache = utils.Cache(CACHE_FILE_PATH)
    assert cache.get('mykey') is None


def test_cache_get_should_return_value():
    os.mkdir(CACHE_DIR)
    with open(CACHE_FILE_PATH, 'w') as fout:
        data = fixture_cache_data()
        payload = yaml.dump(data, default_flow_style=False)
        fout.write(payload)
    cache = utils.Cache(CACHE_FILE_PATH)
    assert cache.get('mykey') == 'myvalue'


def test_cache_get_should_return_none_if_entry_is_expired():
    os.mkdir(CACHE_DIR)
    with open(CACHE_FILE_PATH, 'w') as fout:
        data = fixture_cache_data()
        data['mykey']['expires'] -= timedelta(seconds=120)
        payload = yaml.dump(data, default_flow_style=False)
        fout.write(payload)
    cache = utils.Cache(CACHE_FILE_PATH)
    assert cache.get('mykey') is None


def test_cache_set_should_make_cache_file():
    cache = utils.Cache(CACHE_FILE_PATH)
    cache.set('mykey', True)
    assert os.path.isfile(CACHE_FILE_PATH)


def test_cache_set_should_make_entry_in_cache_file():
    cache = utils.Cache(CACHE_FILE_PATH)
    cache.set('mykey', True)
    with open(CACHE_FILE_PATH) as fin:
        data = yaml.load(fin.read())
        assert data['mykey']['value'] is True


def test_cache_set_should_work_with_existing_cache_file():
    cache = utils.Cache(CACHE_FILE_PATH)
    with open(CACHE_FILE_PATH, 'w') as fout:
        data = fixture_cache_data()
        payload = yaml.dump(data, default_flow_style=False)
        fout.write(payload)

    cache.set('mykey2', False)
    with open(CACHE_FILE_PATH) as fin:
        data = yaml.load(fin.read())
        assert data['mykey2']['value'] is False


def test_write_content_to_file_should_write_file():
    path = os.path.join('test_result', 'writetest.txt')
    if os.path.isfile(path):
        os.remove(path)

    utils.write_content_to_file(path, 'write test')
    assert os.path.isfile(path) is True
    os.remove(path)


def test_read_content_from_file_should_read_content():
    assert utils.read_content_from_file('fixtures/testfile.txt') == 'this is a test file\n'


def test_find_versions():
    with open('fixtures/pypi-versions.txt') as fin:
        content = fin.read()

    assert utils.find_versions(content) == set(['0.1.3', '0.1.4', '0.1.6', '0.1.7'])


def test_cmp_versions():
    assert utils.cmp_versions('0.1.1', '0.1.3') == -1
    assert utils.cmp_versions('0.1.10', '0.1.3') == 1
    assert utils.cmp_versions('0.2.10', '0.1.3') == 1
    assert utils.cmp_versions('0.2.10', '1.1.3') == -1
    assert utils.cmp_versions('0.2.10', '0.2.10') == 0


def test_get_latest_version():
    versions = set(['0.1.2', '0.1.10', '0.2.1'])
    assert utils.get_latest_version(versions) == '0.2.1'


def test_get_latest_version_from_pypi_should_return_a_version():
    with open('fixtures/pypi-versions.txt') as fin:
        content = fin.read()

    with requests_mock.mock() as m:
        m.get('https://pypi.python.org/simple/bothub-cli', text=content)
        version = utils.get_latest_version_from_pypi(use_cache=False)
        assert version == '0.1.7'


def test_timestamp_should_return_int():
    assert isinstance(utils.timestamp(), int)
