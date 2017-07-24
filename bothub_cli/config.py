# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
import codecs

import yaml
from bothub_cli import exceptions as exc

from six import string_types
from six.moves.configparser import ConfigParser


class ConfigBase(object):
    def __init__(self, path=None):
        self.config = {}
        self.path = Config.determine_path(path)

    @staticmethod
    def determine_path(path):
        # if path is not list, make sure parent dir exists and return
        if isinstance(path, string_types):
            Config.make_parent_dir(path)
            return path

        # if path is list or tuple, iterate to lookup existing path,
        # if not found, try to make empty one with first entry
        if isinstance(path, (list, tuple)):
            for path_candidate in path:
                if os.path.isfile(path_candidate):
                    return path_candidate

            path_to_create = path[0]
            Config.make_parent_dir(path_to_create)
            return path_to_create

        raise exc.ConfigFileNotFound(path)

    @staticmethod
    def make_parent_dir(path):
        parent_dir = os.path.dirname(path)
        if len(parent_dir) > 0 and not os.path.isdir(parent_dir):
            os.makedirs(parent_dir)

    def load(self):
        try:
            with open(self.path) as fin:
                self.config = yaml.load(fin)
        except IOError:
            raise exc.ImproperlyConfigured()

    def save(self):
        with codecs.open(self.path, 'wb', encoding='utf8') as fout:
            content = yaml.dump(self.config, default_flow_style=False)
            fout.write(content)

    def set(self, key, value):
        self.config[key] = value

    def get(self, key):
        return self.config.get(key)


class Config(ConfigBase):
    def __init__(self, path=None):
        _path = path or os.path.expanduser(os.path.join('~', '.bothub', 'config.yml'))
        super(Config, self).__init__(_path)


class ProjectConfig(ConfigBase):
    def __init__(self, path=('bothub.yml', 'bothub.yaml')):
        super(ProjectConfig, self).__init__(path)


class ProjectMeta(ConfigBase):
    def __init__(self, path=os.path.join('.bothub-meta', 'meta.yml')):
        super(ProjectMeta, self).__init__(path)
