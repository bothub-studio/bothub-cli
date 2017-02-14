# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)

from bothub_cli.api import Api
from bothub_cli.config import Config


API = Api()
CONFIG = Config()


def authenticate(username, password):
    token = API.authenticate(username, password)
    CONFIG.set('default', 'auth_token', token)
