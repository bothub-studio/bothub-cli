# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)


class CliException(Exception):
    pass


class InvalidCredential(CliException):
    pass


class NotFound(CliException):
    pass


class NoCredential(CliException):
    pass


class Duplicated(CliException):
    pass


class Cancel(CliException):
    pass


class ImproperlyConfigured(CliException):
    pass


class InvalidValue(CliException):
    pass


class ModuleLoadException(CliException):
    pass
