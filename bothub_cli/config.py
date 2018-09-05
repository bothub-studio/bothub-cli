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
            return path

        # if path is list or tuple, iterate to lookup existing path,
        # if not found, try to make empty one with first entry
        if isinstance(path, (list, tuple)):
            for path_candidate in path:
                if os.path.isfile(path_candidate):
                    return path_candidate

            path_to_create = path[0]
            return path_to_create

        raise exc.ConfigFileNotFound(path)

    @staticmethod
    def make_parent_dir(path):
        parent_dir = os.path.dirname(path)
        if len(parent_dir) > 0 and not os.path.isdir(parent_dir):
            os.makedirs(parent_dir)

    def load(self):
        try:
            with open(self.path, encoding='utf8') as fin:
                self.config = yaml.load(fin)
        except IOError:
            raise exc.ImproperlyConfigured()

    def save(self, target_dir=None):
        _path = os.path.join(target_dir, self.path) if target_dir else self.path
        Config.make_parent_dir(_path)
        with codecs.open(_path, 'wb', encoding='utf8') as fout:
            content = yaml.dump(self.config, default_flow_style=False)
            fout.write(content)

    def set(self, key, value):
        self.config[key] = value

    def get(self, key):
        return self.config.get(key)

    def __setitem__(self, key, value):
        self.set(key, value)

    def __getitem__(self, key):
        return self.get(key)

    def __contains__(self, key):
        return key in self.config

    def __delitem__(self, key):
        del self.config[key]

    def is_exists(self):
        return os.path.isfile(self.path)


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

    def migrate_from_project_config(self, project_config):
        project_id = project_config.get('id')
        if project_id:
            self.set('id', project_id)
            del project_config['id']
            self.save()
            project_config.save()
        project_name = project_config.get('name')
        if project_name:
            self.set('name', project_name)
            del project_config['name']
            self.save()
            project_config.save()
