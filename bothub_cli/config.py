# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
import codecs

import yaml
from .exceptions import NotFound

from six.moves.configparser import ConfigParser


class Config(object):
    path = None

    def __init__(self, path=None):
        self.config = {}
        _path = path or os.path.expanduser(os.path.join('~', '.bothub', 'config.yml'))
        path_list = _path if isinstance(_path, (list, tuple)) else [_path]

        last_path = None

        for path_candidate in path_list:
            last_path = path_candidate
            if os.path.isfile(path_candidate):
                self.path = path_candidate
                break
        if not self.path:
            self.path = last_path

        parent_dir = os.path.dirname(self.path)
        if len(parent_dir) > 0 and not os.path.isdir(parent_dir):
            os.makedirs(parent_dir)

    def load(self):
        with open(self.path) as fin:
            self.config = yaml.load(fin)

    def save(self):
        with codecs.open(self.path, 'wb', encoding='utf8') as fout:
            content = yaml.dump(self.config, default_flow_style=False)
            fout.write(content)

    def set(self, key, value):
        self.config[key] = value

    def get(self, key):
        return self.config.get(key)


class ProjectConfig(Config):
    def __init__(self, path=['bothub.yml', 'bothub.yaml']):
        super(ProjectConfig, self).__init__(path)
