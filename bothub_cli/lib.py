# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
import sys
import json
import time
import traceback
import yaml
import zipfile, shutil
import dialogflow
import io
import google.auth.exceptions
import google.api_core.exceptions

from prompt_toolkit import prompt
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory

from bothub_client.clients import NluClientFactory

from bothub_cli import exceptions as exc
from bothub_cli.api import Api
from bothub_cli.config import Config
from bothub_cli.config import ProjectConfig
from bothub_cli.config import ProjectMeta
from bothub_cli.clients import ConsoleChannelClient
from bothub_cli.clients import CachedStorageClient
from bothub_cli.clients import ExternalHttpStorageClient
from bothub_cli.utils import safe_mkdir
from bothub_cli.utils import read_content_from_file
from bothub_cli.utils import make_dist_package
from bothub_cli.utils import extract_dist_package
from bothub_cli.utils import make_event
from bothub_cli.utils import tabulate_dict
from bothub_cli.utils import get_bot_class
from bothub_cli.utils import make_intents_json
from bothub_cli.utils import make_intents_yml
from bothub_cli.utils import make_entities_json
from bothub_cli.utils import make_entities_yml
from bothub_cli.utils import make_etc_json
from bothub_cli.utils import make_etc_yml


class Cli(object):
    '''A CLI class represents '''
    def __init__(self, api=None, config=None, project_config=None, project_meta=None, print_error=None, print_message=None):
        self.api = api or Api()
        self.config = config or Config()
        self.project_config = project_config or ProjectConfig()
        self.project_meta = project_meta or ProjectMeta()
        if not self.project_meta.is_exists() and self.project_config.is_exists():
            self.project_config.load()
            self.project_meta.migrate_from_project_config(self.project_config)

        self.print_error = print_error or print
        self.print_message = print_message or print

    def authenticate(self, username, password):
        token = self.api.authenticate(username, password)
        self.config.set('auth_token', token)
        self.config.save()

    def init(self, name, description, target_dir=None):
        _target_dir = target_dir or name

        if os.path.isdir(_target_dir) and _target_dir != '.':
            raise exc.TargetDirectoryDuplicated(_target_dir)

        self._load_auth()
        project = self.api.create_project(name, description)
        project_id = project['id']
        programming_language = 'python3'
        self.project_meta.set('id', project_id)
        self.project_meta.set('name', name)
        self.project_meta.save(_target_dir)

        self.project_config.set('programming-language', programming_language)
        self.project_config.save(_target_dir)

    def init_code(self):
        project_id = self.project_meta.get('id')
        programming_language = self.project_config.get('programming-language')
        self.api.upload_code(project_id, programming_language)

    def get_project(self, project_id):
        self._load_auth()
        return self.api.get_project(project_id)

    def ls(self, verbose=False):
        self._load_auth()
        projects = self.api.list_projects()
        args = ('name',) if not verbose else ('name', 'status', 'regdate')
        result = tabulate_dict(projects, *args)
        return result

    def rm(self, name):
        self._load_auth()
        projects = self.api.list_projects()
        _projects = [p for p in projects if p['name'] == name]
        if not _projects:
            raise exc.ProjectNameNotFound(name)
        for project in _projects:
            self.api.delete_project(project['id'])

    def deploy(self, console=None, source_dir='.', max_retries=30):
        self._load_auth()
        self.project_config.load()

        safe_mkdir('dist')
        dist_file_path = os.path.join('dist', 'bot.tgz')
        if console:
            console('Make dist package.')
        if os.path.isfile('.bothubignore'):
            make_dist_package(dist_file_path, source_dir, ignores=True)
        else:
            make_dist_package(dist_file_path, source_dir)

        if console:
            console('Upload code', nl=False)
        with open(dist_file_path, 'rb') as dist_file:
            dependency = read_content_from_file('requirements.txt') or 'bothub'
            project_id = self._get_current_project_id()
            self.api.upload_code(
                project_id,
                self.project_config.get('programming-language'),
                dist_file,
                dependency
            )
        self._wait_deploy_completion(project_id, console, max_retries=max_retries)

    def clone(self, project_name, target_dir=None, create_dir=None):
        _target_dir = target_dir or project_name

        if create_dir:
            if os.path.isdir(_target_dir) and _target_dir != '.':
                raise exc.TargetDirectoryDuplicated(_target_dir)

        self._load_auth()
        project_id = self._get_project_id_with_name(project_name)
        self.project_meta.set('id', project_id)
        self.project_meta.set('name', project_name)
        self.project_meta.save(_target_dir)
        response = self.api.get_code(project_id)
        code = response['code']
        code_byte = eval(code) if code[0] == 'b' else code

        with open('code.tgz', 'wb') as code_file:
            code_file.write(code_byte)

        extract_dist_package('code.tgz', _target_dir)
        if os.path.isfile('code.tgz'):
            os.remove('code.tgz')

    def add_channel(self, channel, credentials):
        self._load_auth()
        project_id = self._get_current_project_id()
        self.api.add_project_channel(project_id, channel, credentials)
        if channel == 'kakao' or channel == 'twilio':
            return "Please input below url to {} setting page.\n\n \
            URL: {}\n".format(channel.capitalize(), self.api.get_webhook_url(channel, project_id))
        elif channel == 'line':
            result = []
            result.append('Please input below url to {} setting page\n\n'.format(channel.capitalize()))
            result.append('\t- Webhook URL: {}\n'.format(self.api.get_webhook_url(channel, project_id)))
            return '\n'.join(result)
        elif channel == 'slack':
            result = []
            result.append('Please input below url to {} setting page\n\n'.format(channel.capitalize()))
            result.append('\t- Event Subscriptions URL: {}'.format(self.api.get_webhook_url(channel, project_id)))
            result.append('\t- Interactivity URL: {}/action'.format(self.api.get_webhook_url(channel, project_id)))
            result.append('\t- Redirect URL: {}/oauth_callback\n'.format(self.api.get_webhook_url(channel, project_id)))
            return '\n'.join(result)

    def ls_channel(self, verbose=False):
        self._load_auth()
        project_id = self._get_current_project_id()
        channels = self.api.get_project_channels(project_id)
        args = ('channel',) if not verbose else ('channel', 'credentials')
        result = tabulate_dict(channels, *args)
        return result

    def rm_channel(self, channel):
        self._load_auth()
        project_id = self._get_current_project_id()
        self.api.delete_project_channels(project_id, channel)

    def ls_properties(self):
        self._load_auth()
        project_id = self._get_current_project_id()
        return self.api.get_project_property(project_id)

    def get_properties(self, key):
        self._load_auth()
        project_id = self._get_current_project_id()
        data = self.api.get_project_property(project_id)
        return data[key]

    def set_properties(self, key, value):
        try:
            _value = json.loads(value)
        except ValueError:
            _value = value

        self._load_auth()
        project_id = self._get_current_project_id()
        return self.api.set_project_property(project_id, key, _value)

    def rm_properties(self, key):
        self._load_auth()
        project_id = self._get_current_project_id()
        self.api.delete_project_property(project_id, key)

    def read_property_file(self, file):
        try:
            return yaml.load(file)
        except:
            raise exc.InvalidJsonFormat()

    def show_help(self):
        self.print_message()
        self.print_message("Bothub Test Console")
        self.print_message("-------------------")
        self.print_message()
        self.print_message("Commands:")
        self.print_message()
        commands = [
            ("help", "Print help menu"),
            ("updateproperties", "Update local project properties from server"),
            ("exit", "Exit the test console"),
        ]
        max_command_length = max([len(command) for command, _ in commands])
        template_string = "  /{0}{2}{1}"
        for command, description in commands:
            padding_width = (max_command_length - len(command)) + 2 # 2 is extra spaces
            padding = ' ' * padding_width
            self.print_message(template_string.format(command, description, padding))
        self.print_message()

    def test(self):
        self._load_auth()
        history = FileHistory('.history')
        session = PromptSession(history=history)

        project_id = self._get_current_project_id()
        bot_meta = self._load_bot()
        bot = bot_meta['bot']
        storage_client = bot_meta['storage_client'] # type: CachedStorageClient
        self.show_help()
        storage_client.load_project_data()
        while True:
            try:
                line = session.prompt('BotHub> ')
                if not line:
                    continue
                if line.startswith('/help'):
                    self.show_help()
                elif line.startswith('/updateproperties'):
                    storage_client.load_project_data()
                elif line.startswith('/exit'):
                    break
                else:
                    event = make_event(line)
                    context = {}
                    bot.handle_message(event, context)
            except (EOFError, KeyboardInterrupt):
                break
            except Exception:
                traceback.print_exc()

    def add_nlu(self, nlu, credentials):
        self._load_auth()
        project_id = self._get_current_project_id()
        self.api.add_project_nlu(project_id, nlu, credentials)

    def ls_nlus(self, verbose=False):
        self._load_auth()
        project_id = self._get_current_project_id()
        nlus = self.api.get_project_nlus(project_id)
        args = ('nlu',) if not verbose else ('nlu', 'credentials')
        result = tabulate_dict(nlus, *args)
        return result

    def rm_nlu(self, nlu):
        self._load_auth()
        project_id = self._get_current_project_id()
        self.api.delete_project_nlu(project_id, nlu)

    def logs(self):
        self._load_auth()
        project_id = self._get_current_project_id()
        logs = self.api.get_project_execution_logs(project_id)
        return sorted(logs, key=lambda x: x['regdate'])

    def _load_auth(self):
        '''Load auth token from bothub config and inject to API class'''
        self.config.load()
        self.api.load_auth(self.config)

    def _get_current_project_id(self):
        self.project_meta.load()
        project_id = self.project_meta.get('id')
        if not project_id:
            raise exc.ImproperlyConfigured()
        return project_id

    def _get_project_id_with_name(self, project_name):
        self._load_auth()
        projects = self.api.list_projects()
        for p in projects:
            if p['name'] == project_name:
                return p['id']
        raise exc.ProjectNameNotFound(project_name)

    def _wait_deploy_completion(self, project_id, console, wait_interval=1, max_retries=30):
        first_deploying_dot = True
        for _ in range(max_retries):
            project = self.api.get_project(project_id)
            if project['status'] == 'online':
                if console:
                    console('.')
                return

            if project['status'] == 'deploying' and console:
                if first_deploying_dot:
                    console('.')
                    console('Restarting container', nl=False)
                    first_deploying_dot = False

            if console:
                console('.', nl=False)
            time.sleep(wait_interval)
        raise exc.DeployFailed()

    def _load_bot(self, target_dir='.'):
        project_id = self._get_current_project_id()
        event = {
            'sender': {
                'id': '-1'
            },
            'channel': 'console'
        }
        context = {}
        nlus = self.api.get_project_nlus(project_id)
        context['nlu'] = dict([(nlu['nlu'], nlu['credentials']) for nlu in nlus])

        channel_client = ConsoleChannelClient()
        http_storage_client = ExternalHttpStorageClient(
            self.config.get('auth_token'),
            project_id,
        )
        storage_client = CachedStorageClient(http_storage_client)
        nlu_client_factory = NluClientFactory(context)
        bot_class = get_bot_class(target_dir)
        bot = bot_class(
            channel_client=channel_client,
            storage_client=storage_client,
            nlu_client_factory=nlu_client_factory,
            event=event
        )
        return {'bot': bot, 'channel_client': channel_client, 'storage_client': storage_client,
                'nlu_client_factory': nlu_client_factory}

    def get_credential(self, nlu):
        self._load_auth()
        project_id = self._get_current_project_id()
        nlu = self.api.get_project_nlu(project_id, nlu)
        return nlu['credentials']

    def push_agent(self):
        agent_id = self.get_credential('dialogflow')['agent_id']
        client = dialogflow.AgentsClient()
        parent = client.project_path(agent_id)
        response = client.get_agent(parent)
        agent_name = response.display_name
        agent_folder = os.path.join("./dialogflow", agent_name)

        try:
            self._yml2json(agent_name, agent_id)
            with zipfile.ZipFile(agent_folder + '.zip', 'w') as myzip:
                for folder, subfolders, files in os.walk(agent_folder):
                    for f in subfolders + files:
                        if not f.endswith(".yml"):
                            absname = os.path.join(folder, f)
                            arcname = absname.replace("/dialogflow", "")
                            myzip.write(absname, arcname)
            self._upload_agent(agent_name, agent_id)
        except google.api_core.exceptions.InvalidArgument:
            raise exc.InvalidYamlFormat()
        except TypeError:
            raise exc.InvalidYamlFormat()

    def pull_agent(self, agent_id=None):
        try:
            if not agent_id:
                agent_id = self.get_credential('dialogflow')['agent_id']
            client = dialogflow.AgentsClient()
            parent = client.project_path(agent_id)
            response = client.get_agent(parent)
            agent_name = response.display_name
            if not os.path.exists("./dialogflow"):
                os.mkdir("./dialogflow")

            self._download_agent(agent_name, agent_id)
            self._json2yml(agent_name, agent_id)
        except google.api_core.exceptions.PermissionDenied:
            raise exc.InvalidAgentId(agent_id)
        except google.auth.exceptions.DefaultCredentialsError:
            raise exc.InvalidCredentialPath()

    def isValidAgentId(self, agent_id):
        client = dialogflow.AgentsClient()
        parent = client.project_path(agent_id)
        response = client.get_agent(parent)

    def _upload_agent(self, agent_name, agent_id):
        client = dialogflow.AgentsClient()
        parent = client.project_path(agent_id)

        in_file = open(os.path.join("./dialogflow", agent_name + ".zip"), "rb")
        data = in_file.read()
        response = client.restore_agent(parent, agent_content=data)

    def _download_agent(self, agent_name, agent_id):
        client = dialogflow.AgentsClient()
        parent = client.project_path(agent_id)

        agent_folder = os.path.join("./dialogflow", agent_name)
        if os.path.exists(agent_folder):
            shutil.rmtree(agent_folder)
        os.mkdir(agent_folder)

        response = client.export_agent(parent).operation.response.value
        zip_file = zipfile.ZipFile(io.BytesIO(response), "r")
        for filename in zip_file.namelist():
            split_name = filename.split('/')
            for name in split_name[:-1]:
                if not os.path.exists(os.path.join(agent_folder, name)):
                    os.mkdir(os.path.join(agent_folder, name))
            with open(os.path.join(agent_folder, filename), "wb") as f:
                f.write(zip_file.read(filename))

    def _yml2json(self, agent_name, agent_id):
        agent_folder = os.path.join("./dialogflow", agent_name)
        lang = self._get_dialogflow_lang(agent_id)

        package_path = os.path.join(agent_folder, "package.json")
        if os.path.exists(package_path):
            os.remove(package_path)
        agent_path = os.path.join(agent_folder, "agent.json")
        if os.path.exists(agent_path):
            os.remove(agent_path)

        if os.path.exists(os.path.join(agent_folder, "intents")):
            shutil.rmtree(os.path.join(agent_folder, "intents"))
        os.mkdir(os.path.join(agent_folder, "intents"))

        with open(os.path.join(agent_folder, "intents.yml"), "r") as stream:
            intents_docs = yaml.load_all(stream) 
            for doc in intents_docs:
                for key, value in doc.items():
                    make_intents_json(agent_folder, key, value, lang)
        if os.path.exists(os.path.join(agent_folder, "entities")):
            shutil.rmtree(os.path.join(agent_folder, "entities"))
        os.mkdir(os.path.join(agent_folder, "entities"))
        with open(os.path.join(agent_folder, "entities.yml"), "r") as stream:
            entities_docs = yaml.load_all(stream)
            for doc in entities_docs:
                for key, value in doc.items():
                    make_entities_json(agent_folder, key, value, lang)
        make_etc_json(agent_folder)

    def _json2yml(self, agent_name, agent_id):
        agent_folder = os.path.join("./dialogflow", agent_name)
        lang = self._get_dialogflow_lang(agent_id)

        make_intents_yml(agent_folder, lang)
        make_entities_yml(agent_folder, lang)
        make_etc_yml(agent_folder)

    def _get_dialogflow_lang(self, agent_id):
        client = dialogflow.AgentsClient()
        parent = client.project_path(agent_id)
        response = client.get_agent(parent)
        lang = response.default_language_code
        return lang
