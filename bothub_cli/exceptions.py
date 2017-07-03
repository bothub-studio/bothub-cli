# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)


class CliException(Exception):
    pass


class InvalidCredential(CliException):
    pass


class NotFound(CliException):
    pass


class UserNotFound(NotFound):
    def __init__(self, username):
        msg = "No such user: {}.".format(username)
        super(UserNotFound, self).__init__(msg)


class ProjectIdNotFound(NotFound):
    def __init__(self, project_id):
        msg = "No such project ID: {}.".format(project_id)
        super(ProjectIdNotFound, self).__init__(msg)


class ProjectNameNotFound(NotFound):
    def __init__(self, project_name):
        msg = "No such project name: {}.".format(project_name)
        super(ProjectNameNotFound, self).__init__(msg)


class AuthenticationFailed(InvalidCredential):
    def __init__(self):
        msg = 'Invalid username or password.'
        super(AuthenticationFailed, self).__init__(msg)


class NoCredential(CliException):
    pass


class Duplicated(CliException):
    pass


class ProjectNameDuplicated(Duplicated):
    def __init__(self, name):
        _msg = "Project name {} already exists. Please use other name.".format(name)
        super(ProjectNameDuplicated, self).__init__(_msg)


class Cancel(CliException):
    pass


class ImproperlyConfigured(CliException):
    def __init__(self, msg=None):
        _msg = msg or "Invalid project directory. "\
               "Is this a valid bothub project directory?"
        super(ImproperlyConfigured, self).__init__(_msg)


class InvalidValue(CliException):
    pass


class ModuleLoadException(CliException):
    def __init__(self):
        msg = "Couldn't found a valid bothub app on bothub/bot.py."
        super(ModuleLoadException, self).__init__(msg)


class Timeout(CliException):
    pass


class AuthTokenExpired(CliException):
    def __init__(self, msg=None):
        _msg = msg or "Login credentials have expired. "\
               "Please try 'bothub configure' to refresh login credentials."
        super(AuthTokenExpired, self).__init__(_msg)


class DeployFailed(CliException):
    def __init__(self):
        msg = 'Deploy has failed'
        super(DeployFailed, self).__init__(msg)


class NotLatestVersion(CliException):
    def __init__(self, current_version, latest_version):
        msg = "New bothub-cli version has detected. You have {} and pypi has {}. "\
              "Please upgrade the package: 'pip install --upgrade bothub-cli'.".format(
                  current_version,
                  latest_version
              )
        super(NotLatestVersion, self).__init__(msg)
