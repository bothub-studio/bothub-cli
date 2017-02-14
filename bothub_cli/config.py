# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
import codecs
from six.moves.configparser import ConfigParser


class Config(object):
    def __init__(self, path=None):
        self.config = ConfigParser()
        self.path = path or os.path.expanduser(os.path.join('.bothub', 'config.ini'))
        parent_dir = os.path.dirname(self.path)
        if not os.path.isdir(parent_dir):
            os.makedirs(parent_dir)

        self.init_sections()

    def init_sections(self):
        if not self.config.has_section('default'):
            self.config.add_section('default')

    def load(self):
        self.config.read(self.path)
        self.init_sections()

    def save(self):
        with codecs.open(self.path, 'wb', encoding='utf8') as fp:
            self.config.write(fp)

    def set(self, section, key, value):
        self.config.set(section, key, value)

    def get(self, section, key):
        return self.config.get(section, key)
