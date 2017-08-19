# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
import re
import sys
import time
from datetime import datetime
from datetime import timedelta
import yaml
import requests
import tarfile

from bothub_cli import __version__
from bothub_cli import exceptions as exc

PYPI_VERSION_PATTERN = re.compile(r'bothub_cli-(.+?)-py2.py3-none-any.whl')
PACKAGE_IGNORE_PATTERN = [
    re.compile('.bothub-meta'),
    re.compile('dist'),
    re.compile('.*\.pyc'),
    re.compile('.*/__pycache__/.*'),
]


class Cache(object):
    def __init__(self, path=None):
        self.cache_path = path or os.path.expanduser(os.path.join('~', '.bothub', 'caches.yml'))
        parent_path = os.path.dirname(self.cache_path)
        if not os.path.isdir(parent_path):
            os.makedirs(parent_path)

    def get(self, key):
        if not os.path.isfile(self.cache_path):
            return None
        content = read_content_from_file(self.cache_path)
        cache_entry = yaml.load(content)
        if not cache_entry:
            return None
        entry = cache_entry[key]
        now = datetime.now()
        if now > entry['expires']:
            return None
        return entry['value']

    def set(self, key, value, ttl=3600):
        if not os.path.isfile(self.cache_path):
            cache_obj = {}
        else:
            content = read_content_from_file(self.cache_path)
            cache_obj = yaml.load(content)
            if not cache_obj:
                cache_obj = {}
        cache_entry = cache_obj.setdefault(key, {})
        cache_entry['value'] = value
        cache_entry['expires'] = datetime.now() + timedelta(seconds=ttl)
        write_content_to_file(self.cache_path, yaml.dump(cache_obj, default_flow_style=False))


def safe_mkdir(path):
    if not os.path.isdir(path):
        os.mkdir(path)


def write_content_to_file(path, content):
    with open(path, 'w') as fout:
        fout.write(content)


def read_content_from_file(path):
    if os.path.isfile(path):
        with open(path) as fin:
            return fin.read()


def find_versions(content):
    return set(PYPI_VERSION_PATTERN.findall(content))


def cmp_versions(a, b):
    version_a = tuple([int(e) for e in a.split('.')])
    version_b = tuple([int(e) for e in b.split('.')])

    if version_a > version_b:
        return 1
    if version_a < version_b:
        return -1
    return 0


def get_latest_version(versions):
    sorted_versions = sorted(versions, key=lambda v: tuple([int(e) for e in v.split('.')]), reverse=True)
    return sorted_versions[0]


def get_latest_version_from_pypi(use_cache=True, cache=None):
    try:
        if use_cache:
            _cache = cache or Cache()
            latest_version = _cache.get('latest_pypi_version')
            if latest_version:
                return latest_version
        response = requests.get('https://pypi.python.org/simple/bothub-cli', timeout=2)
        content = response.content.decode('utf8')
        versions = find_versions(content)
        latest_version = get_latest_version(versions)
        if use_cache:
            _cache.set('latest_pypi_version', latest_version)
        return latest_version
    except requests.exceptions.Timeout:
        raise exc.Timeout()


def check_latest_version():
    try:
        pypi_version = get_latest_version_from_pypi()
        is_latest = cmp_versions(__version__, pypi_version) >= 0
        if not is_latest:
            raise exc.NotLatestVersion(__version__, pypi_version)

    except exc.Timeout:
        pass


def timestamp(dt=None):
    dt = dt or datetime.utcnow()
    return int(time.mktime(dt.timetuple()))


def check_ignore_pattern(name, soft_ignore_patterns=None):
    if name in soft_ignore_patterns:
        raise exc.IgnorePatternMatched()

    for pattern in PACKAGE_IGNORE_PATTERN:
        if pattern.match(name):
            raise exc.IgnorePatternMatched()


def make_dist_package(dist_file_path, source_dir='.', ignores=tuple()):
    '''Make dist package file of current project directory.
    Includes all files of current dir, bothub dir and tests dir.
    Dist file is compressed with tar+gzip.'''
    if os.path.isfile(dist_file_path):
        os.remove(dist_file_path)

    with tarfile.open(dist_file_path, 'w:gz') as tout:
        for fname in os.listdir(source_dir):
            try:
                check_ignore_pattern(fname, soft_ignore_patterns=ignores)
                if os.path.isfile(fname):
                    tout.add(fname)
                elif os.path.isdir(fname):
                    tout.add(fname)
            except exc.IgnorePatternMatched:
                pass


def extract_dist_package(dist_file_path, target_dir=None):
    '''Extract dist package file to current directory.'''
    _target_dir = target_dir or '.'

    with tarfile.open(dist_file_path, 'r:gz') as tin:
        tin.extractall(_target_dir)


def make_event(message):
    '''Make dummy event for test mode.'''
    data = {
        'trigger': 'cli',
        'channel': 'cli',
        'sender': {
            'id': 'localuser',
            'name': 'Local user'
        },
        'raw_data': message
    }

    if message.startswith('/location'):
        _, latitude, longitude = message.split()
        data['location'] = {
            'latitude': latitude,
            'longitude': longitude
        }
    elif message:
        data['content'] = message

    return data


def tabulate_dict(lst, *fields):
    result = [None] * len(lst)
    for row_idx, row in enumerate(lst):
        row_result = [None] * len(fields)
        for col_idx, field in enumerate(fields):
            row_result[col_idx] = row[field]
        result[row_idx] = row_result
    return result


def get_bot_class(target_dir='.'):
    try:
        sys.path.append(target_dir)
        __import__('bothub.bot')
        mod = sys.modules['bothub.bot']
        return mod.Bot
    except ImportError:
        if sys.exc_info()[-1].tb_next:
            raise
        else:
            raise exc.ModuleLoadException()


def load_readline(history_file_path='.history'):
    try:
        readline = __import__('readline')
        if os.path.isfile(history_file_path):
            readline.read_history_file(history_file_path)
        return readline
    except ImportError:
        pass


def close_readline(history_file_path='.history'):
    try:
        readline = __import__('readline')
        readline.write_history_file(history_file_path)
    except ImportError:
        pass

