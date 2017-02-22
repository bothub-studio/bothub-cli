# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)

import os


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
