# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
import re
import time
from datetime import datetime
from datetime import timedelta
import yaml
import requests

from bothub_cli import exceptions as exc

PYPI_VERSION_PATTERN = re.compile(r'bothub_cli-(.+?)-py2.py3-none-any.whl')


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


def get_latest_version_from_pypi():
    try:
        cache = Cache()
        latest_version = cache.get('latest_pypi_version')
        if latest_version:
            return latest_version
        response = requests.get('https://pypi.python.org/simple/bothub-cli', timeout=2)
        content = response.content.decode('utf8')
        versions = find_versions(content)
        latest_version = get_latest_version(versions)
        cache.set('latest_pypi_version', latest_version)
        return latest_version
    except requests.exceptions.Timeout:
        raise exc.Timeout()
