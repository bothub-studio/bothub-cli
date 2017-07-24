# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)


class MockTransport(object):
    def __init__(self):
        self.response = []
        self.called = []

    def record(self, data):
        self.response.append(data)

    def post(self, *args, **kwargs):
        self.called.append(('post', args, kwargs))
        return self.response.pop(0)

    def get(self, *args, **kwargs):
        self.called.append(('get', args, kwargs))
        return self.response.pop(0)

    def put(self, *args, **kwargs):
        self.called.append(('put', args, kwargs))
        return self.response.pop(0)

    def delete(self, *args, **kwargs):
        self.called.append(('delete', args, kwargs))
        return self.response.pop(0)


class MockResponse(object):
    def __init__(self, body, status_code=200):
        self.body = body
        self.status_code = status_code

    def json(self):
        return self.body


class MockApi(object):
    def __init__(self):
        self.executed = []
        self.responses = []

    def get_project(self, project_id):
        self.executed.append(('get_project', project_id))
        return self.responses.pop(0)

    def load_auth(self, config):
        pass

    def list_projects(self):
        self.executed.append(('list_project', ))
        return self.responses.pop(0)

    def delete_project(self, name):
        self.executed.append(('delete_project', name))
        return self.responses.pop(0)

    def upload_code(self, project_id, language, dist_file, dependency):
        self.executed.append(('upload_code', project_id, language, dist_file.read(), dependency))
        return self.responses.pop(0)

    def get_code(self, project_id):
        self.executed.append(('get_code', project_id))
        return self.responses.pop(0)

    def add_project_channel(self, project_id, channel, credentials):
        self.executed.append(('add_project_channel', project_id, channel, credentials))
        return self.responses.pop(0)

    def delete_project_channels(self, project_id, channel):
        self.executed.append(('delete_project_channel', project_id, channel))
        return self.responses.pop(0)

    def get_project_channels(self, project_id):
        self.executed.append(('get_project_channels', project_id))
        return self.responses.pop(0)

    def set_project_property(self, project_id, key, value):
        self.executed.append(('set_project_property', project_id, key, value))
        return self.responses.pop(0)

    def get_project_property(self, project_id):
        self.executed.append(('get_project_property', project_id))
        return self.responses.pop(0)

    def delete_project_property(self, project_id, key):
        self.executed.append(('delete_project_property', project_id, key))
        return self.responses.pop(0)

    def add_project_nlu(self, project_id, nlu, credentials):
        self.executed.append(('add_project_nlu', project_id, nlu, credentials))
        return self.responses.pop(0)

    def get_project_nlus(self, project_id):
        self.executed.append(('get_project_nlus', project_id))
        return self.responses.pop(0)

    def delete_project_nlu(self, project_id, nlu):
        self.executed.append(('delete_project_nlu', project_id, nlu))
        return self.responses.pop(0)
