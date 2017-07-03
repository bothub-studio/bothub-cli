# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
import re
import requests

from bothub_cli import exceptions as exc

PYPI_VERSION_PATTERN = re.compile(r'bothub_cli-(.+?)-py2.py3-none-any.whl')

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
        response = requests.get('https://pypi.python.org/simple/bothub-cli', timeout=2)
        content = response.content.decode('utf8')
        versions = find_versions(content)
        return get_latest_version(versions)
    except requests.exceptions.Timeout:
        raise exc.Timeout()
