# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)
import os
import json
import click
import re

from terminaltables import AsciiTable as Table
try:
    from json import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError

from bothub_cli import __version__
from bothub_cli import lib
from bothub_cli import utils
from bothub_cli import exceptions as exc


def print_error(msg):
    click.secho(msg, fg='red')


def print_success(msg):
    click.secho(msg, fg='green')


def print_message(msg=''):
    click.echo(msg)


def print_introduction(start_line=0):
    commands = [
        ('bothub configure', '-- Configure an account credential'),
        ('bothub new', '-- Create an blank project'),
        ('bothub test', '-- Get into the newly created project directory and run `bothub test`'),
        ('bothub deploy', '-- Write your code in `bot.py` and run `bothub deploy` to deploy it'),
    ]
    click.secho('What you can do next:', fg='green')
    click.secho('')

    for index, (command, description) in enumerate(commands[start_line:], 1):
        click.secho('Step {}: {}'.format(index, command), fg='green')
        click.secho(' ' * 2 + description)


@click.group(invoke_without_command=True)
@click.option('-V', '--version', is_flag=True, default=False)
@click.pass_context
def cli(ctx, version):
    '''Bothub is a command line tool that configure, init,
    and deploy bot codes to BotHub.Studio service'''
    try:
        utils.check_latest_version()
        utils.check_latest_version_sdk()
    except exc.NotLatestVersion as ex:
        click.secho(str(ex), fg='yellow')
    except exc.NotLatestVersionSdk as ex:
        click.secho(str(ex), fg='yellow')

    if version:
        click.secho(__version__)
        return

    if ctx.invoked_subcommand is None:
        print(ctx.get_help())


@cli.command()
def introduction():
    '''
    Introduction Guide
    '''
    print_introduction()


@cli.command()
def configure():
    '''Setup credentials'''
    try:
        click.echo('Please enter your BotHub.Studio login credentials:')
        username = click.prompt('username')
        password = click.prompt('password', hide_input=True)
        click.secho('Connecting to server...', fg='green')
        lib_cli = lib.Cli()
        lib_cli.authenticate(username, password)
        click.secho('Identified. Welcome {}.'.format(username), fg='green')
        click.echo('')
        print_introduction(1)
    except exc.CliException as ex:
        click.secho('{}: {}'.format(ex.__class__.__name__, ex), fg='red')


def create_project(create_dir=False):
    click.echo('Initialize a new project.')
    while True:
        try:
            lib_cli = lib.Cli()
            project_config_exists = lib_cli.project_config.is_exists()
            name = click.prompt('Project name')
            normalized_name = name.strip()
            if not normalized_name:
                continue
            target_dir = '.'
            if create_dir:
                target_dir = normalized_name
            click.secho('Creating project...', fg='green')
            lib_cli.init(normalized_name, '', target_dir=target_dir)

            if not project_config_exists:
                click.secho('Initialize project template.')
                lib_cli.init_code()
                click.secho('Download project template.')
                lib_cli.clone(normalized_name, target_dir=target_dir)
                click.echo('')
            else:
                click.secho('Skip to initialize a project template.')

            click.secho('Project has created.', fg='green')
            break
        except exc.Cancel:
            print_error('Project creation has cancelled.')
            break
        except exc.CliException as ex:
            print_error('{}: {}'.format(ex.__class__.__name__, ex))
            break


@cli.command()
def init():
    '''Initialize project'''
    create_project()
    print_introduction(2)


@cli.command(name='new')
def new_project():
    '''Create new Bothub project'''
    create_project(True)
    print_introduction(2)


@cli.command()
@click.option('--max-retries', default=30)
def deploy(max_retries):
    '''Deploy project'''
    try:
        lib_cli = lib.Cli()
        lib_cli.deploy(console=click.echo, max_retries=max_retries)
        click.secho('Project is deployed.', fg='green')
    except exc.CliException as ex:
        click.secho('{}: {}'.format(ex.__class__.__name__, ex), fg='red')


@cli.command()
@click.argument('project-name')
def clone(project_name):
    '''Clone existing project'''

    try:
        lib_cli = lib.Cli()
        lib_cli.clone(project_name, create_dir=True)
        click.secho('Project {} is cloned.'.format(project_name), fg='green')
    except exc.CliException as ex:
        click.secho('{}: {}'.format(ex.__class__.__name__, ex), fg='red')


@cli.command()
@click.option('-l', '--long', count=True)
def ls(long=False):
    '''List projects'''
    try:
        lib_cli = lib.Cli()
        projects = lib_cli.ls(long)
        header = ['Project']
        if long:
            header += ['Status', 'Created']
        data = [header] + projects
        table = Table(data)
        click.secho(table.table)
        click.secho('You have {} projects'.format(len(projects)))
    except exc.CliException as ex:
        click.secho('{}: {}'.format(ex.__class__.__name__, ex), fg='red')


@cli.command()
@click.argument('name')
def rm(name):
    '''Delete a project'''
    try:
        lib_cli = lib.Cli()
        lib_cli.rm(name)
        click.secho('Deleted a project: {}'.format(name))
    except exc.CliException as ex:
        click.secho('{}: {}'.format(ex.__class__.__name__, ex), fg='red')
    except ValueError as err:
        click.secho('{}'.format(err), fg='red')


@cli.group()
def channel():
    '''Setup channels of current project'''
    pass


def add_option_to_dict(d, option_name, option):
    if option:
        d[option_name] = option


def ask_channel_keys(param_list):
    credentials = {}
    for param in param_list:
        title = param['name'].replace('_', ' ').title()
        valid_msg = ''
        while True:
            matches = re.match(param['rule'], param['value'])
            if matches:
                credentials[param['name']] = matches.group()
                print_success('{} is saved'.format(title))
                break
            elif param['value']:
                valid_msg = ' a valid'
                print_error("{} is invalid".format(title))
            param['value'] = click.prompt(param['prompt'].format(valid_msg, title))
    return credentials


@channel.command(name='add')
@click.argument('channel', default='')
@click.option('--api-key', help='Telegram api key', default='')
@click.option('--app-id', help='Facebook app id', default='')
@click.option('--app-secret', help='Facebook app secret', default='')
@click.option('--page-access-token', help='Facebook page access token', default='')
@click.option('--client-id', help='Slack client id', default='')
@click.option('--client-secret', help='Slack client secret', default='')
@click.option('--signing-secret', help='Slack signing secret', default='')
@click.option('--channel-id', help='Line channel id', default='')
@click.option('--channel-secret', help='Line channel secret', default='')
@click.option('--channel-access-token', help='Line channel access token', default='')
def add_channel(channel, api_key, app_id, app_secret, page_access_token, client_id, client_secret, signing_secret, channel_id, channel_secret, channel_access_token):
    '''Add a new channel to current project'''
    try:
        credentials = {}
        if not channel in ['telegram', 'facebook', 'slack', 'kakao', 'twilio', 'line']:
            channel = click.prompt('Choose a channel to add: [facebook, telegram, slack, kakao, line]', type=click.Choice(['facebook', 'telegram', 'slack', 'kakao', 'line']))

        channel_list = {
            'telegram': [
                {'name': 'api_key', 'value': api_key, 'prompt': 'Please enter{} Telegram {}', 'rule': r'[0-9]{9}:[\w.-]{35}'},
            ],
            'facebook': [
                {'name': 'app_id', 'value': app_id, 'prompt': 'Please enter{} Facebook {}', 'rule': r'[0-9]{6,20}'},
                {'name': 'app_secret', 'value': app_secret, 'prompt': 'Please enter{} Facebook {}', 'rule': r'[a-zA-Z0-9]{12,}'},
                {'name': 'page_access_token', 'value': page_access_token, 'prompt': 'Please enter{} Facebook {}', 'rule': r'[a-zA-Z0-9]{100,}'},
            ],
            'slack': [
                {'name': 'client_id', 'value': client_id, 'prompt': 'Please enter{} Slack {}', 'rule': r'[0-9]{12}\.[0-9]{12}'},
                {'name': 'client_secret', 'value': client_secret, 'prompt': 'Please enter{} Slack {}', 'rule': r'[0-9a-zA-Z]{32}'},
                {'name': 'signing_secret', 'value': signing_secret, 'prompt': 'Please enter{} Slack {}', 'rule': r'^[0-9a-zA-Z]{32}'},
            ],
            'kakao':[
            ],
            'twilio':[
            ],
            'line': [
                {'name': 'channel_id', 'value': channel_id, 'prompt': 'Please enter{} Line {}', 'rule': r'.+'},
                {'name': 'channel_secret', 'value': channel_secret, 'prompt': 'Please enter{} Line {}', 'rule': r'.+'},
                {'name': 'channel_access_token', 'value': channel_access_token, 'prompt': 'Please enter{} Line {}', 'rule': r'^.+'},
            ]
        }

        credentials = ask_channel_keys(channel_list[channel])
        lib_cli = lib.Cli()
        result = lib_cli.add_channel(channel, credentials)
        click.secho('Added a channel {}'.format(channel))

        if channel == 'kakao' or channel == 'slack' or channel == 'line':
            print_success(result)

    except exc.CliException as ex:
        click.secho('{}: {}'.format(ex.__class__.__name__, ex), fg='red')


@channel.command(name='ls')
@click.option('-l', '--long', count=True)
def ls_channel(long=False):
    '''List channels of current project'''
    try:
        lib_cli = lib.Cli()
        channels = lib_cli.ls_channel(long)
        header = ['Channel']
        if long:
            header.append('Credentials')
        data = [header] + channels
        table = Table(data)
        click.secho(table.table)
    except exc.CliException as ex:
        click.secho('{}: {}'.format(ex.__class__.__name__, ex), fg='red')


@channel.command(name='rm')
@click.argument('channel')
def rm_channel(channel):
    '''Remove a channel from current project'''
    try:
        lib_cli = lib.Cli()
        lib_cli.rm_channel(channel)
        click.secho('Deleted a channel: {}'.format(channel))
    except exc.CliException as ex:
        click.secho('{}: {}'.format(ex.__class__.__name__, ex), fg='red')


@cli.group()
def property():
    '''Manage project properties'''
    pass


def print_properties(d):
    width = max([len(k) for k in d.keys()])
    for key, val in d.items():
        click.echo('{0: <{2}}: {1}'.format(key, val, width + 3))


@property.command(name='ls')
def ls_property():
    '''Get property list'''
    try:
        lib_cli = lib.Cli()
        properties = lib_cli.ls_properties()
        properties_list = [(k, v) for k, v in properties.items()]
        header = ['Name', 'Value']
        data = [header] + properties_list
        table = Table(data)
        click.secho(table.table)
    except exc.CliException as ex:
        click.secho('{}: {}'.format(ex.__class__.__name__, ex), fg='red')


@property.command(name='get')
@click.argument('key')
def get_property(key):
    '''Get value of a property'''
    try:
        lib_cli = lib.Cli()
        result = lib_cli.get_properties(key)
        if isinstance(result, dict):
            print_properties(result)
        else:
            click.echo('{}: {}'.format(key, result))
    except KeyError:
        click.secho('No such property: {}'.format(key), fg='red')
    except exc.CliException as ex:
        click.secho('{}: {}'.format(ex.__class__.__name__, ex), fg='red')


@property.command(name='set')
@click.argument('key', default='', )
@click.argument('value', default='')
@click.option('--file', type=click.File('r'))
def set_property(key, value, file):
    '''Set value of a property'''
    try:
        lib_cli = lib.Cli()
        if value:
            lib_cli.set_properties(key, value)
            click.secho("Set a property: {}".format(key))
        elif key and file:
            value = lib_cli.read_property_file(file)
            lib_cli.set_properties(key, str(value))
            click.secho("Set a property: {}".format(key))
        elif file:
            value = lib_cli.read_property_file(file)
            for key in value:
                lib_cli.set_properties(key, str(value[key]))
                click.secho("Set a property: {}".format(key))
        else :
            if not key:
                key = click.prompt('key')
            value = click.prompt('value')
            lib_cli.set_properties(key, value)
            click.secho("Set a property: {}".format(key))
    except exc.CliException as ex:
        click.secho('{}: {}'.format(ex.__class__.__name__, ex), fg='red')


@property.command(name='rm')
@click.argument('key')
def rm_property(key):
    '''Delete a property'''
    try:
        lib_cli = lib.Cli()
        lib_cli.rm_properties(key)
        click.secho("Deleted a property: {}".format(key))
    except exc.CliException as ex:
        click.secho('{}: {}'.format(ex.__class__.__name__, ex), fg='red')


@cli.group()
def nlu():
    '''Manage project NLU integrations'''
    pass


@nlu.command(name='ls')
@click.option('-l', '--long', count=True)
def ls_nlu(long=False):
    '''List NLU integrations'''
    try:
        lib_cli = lib.Cli()
        nlus = lib_cli.ls_nlus(long)
        header = ['NLU']
        if long:
            header.append('Credentials')
        data = [header] + nlus
        table = Table(data)
        click.secho(table.table)
    except exc.CliException as ex:
        click.secho('{}: {}'.format(ex.__class__.__name__, ex), fg='red')


def ask_nlu_keys(param_list):
    credentials = {}
    for param in param_list:
        title = param['name'].replace('_', ' ').title()
        valid_msg = ''
        while True:
            matches = re.match(param['rule'], param['value'])
            if matches:
                credentials[param['name']] = matches.group()
                print_success('{} is saved'.format(title))
                break
            elif param['value']:
                valid_msg = ' a valid'
                print_error("{} is invalid".format(title))
            param['value'] = click.prompt(param['prompt'].format(valid_msg, title))
    return credentials


@nlu.command(name='add')
@click.argument('nlu', default='')
@click.option('--api-key', help='API.ai api key', default='')
@click.option('--agent-id', help='Dialogflow agent id', default='')
def add_nlu(nlu, api_key, agent_id):
    '''Add a NLU integration'''
    try:
        lib_cli = lib.Cli()
        credentials = {}
        if not nlu in ['apiai', 'dialogflow']:
            nlu = click.prompt('Choose a nlu to add: [apiai, dialogflow]', type=click.Choice(['apiai', 'dialogflow']))
        nlu_list = {
            'apiai':[
                {'name': 'api_key', 'value': api_key, 'prompt': 'Please enter{} Api AI {}', 'rule':r'.+'},
            ],
            'dialogflow':[
                {'name': 'agent_id', 'value': agent_id, 'prompt': 'Please enter{} Dialogflow {}', 'rule':r'.+'},
            ],
        }
        credentials = ask_nlu_keys(nlu_list[nlu])
        if nlu == 'dialogflow':
            lib_cli.pull_agent(credentials['agent_id'])
        lib_cli.add_nlu(nlu, credentials)
        click.secho('Added a NLU: {}'.format(nlu))
    except exc.CliException as ex:
        click.secho('{}: {}'.format(ex.__class__.__name__, ex), fg='red')


@nlu.command(name='rm')
@click.argument('nlu')
def rm_nlu(nlu):
    '''Delete a NLU integration'''
    try:
        lib_cli = lib.Cli()
        lib_cli.rm_nlu(nlu)
        click.secho('Deleted a NLU: {}'.format(nlu))
    except exc.CliException as ex:
        click.secho('{}: {}'.format(ex.__class__.__name__, ex), fg='red')


@cli.command(name='test')
def test():
    '''Run test chat session'''
    try:
        lib_cli = lib.Cli(print_message=print_message)
        lib_cli.test()
    except exc.CliException as ex:
        click.secho('{}: {}'.format(ex.__class__.__name__, ex), fg='red')


@cli.command(name='logs')
def logs():
    '''Show error logs'''
    try:
        lib_cli = lib.Cli()
        log_entries = lib_cli.logs()
        for log_entry in log_entries:
            try:
                log_dict = json.loads(log_entry['log'])
                log_message = '{}\n{}'.format(log_dict['error'], log_dict['trace'])
            except JSONDecodeError:
                log_message = log_entry['log']
            click.echo('{} {}'.format(log_entry['regdate'], log_message))
    except exc.CliException as ex:
        click.secho('{}: {}'.format(ex.__class__.__name__, ex), fg='red')


@cli.group()
def dialogflow():
    '''Manage Dialogflow agent'''
    pass


@dialogflow.command(name='push')
def push_agent():
    '''Push agent from local to Dialogflow Server'''
    try:
        lib_cli = lib.Cli()
        lib_cli.push_agent()
        credential = lib_cli.get_credential("dialogflow")
        click.secho('Pushed agent to: {}'.format(credential['agent_id']))
    except exc.CliException as ex:
        click.secho('{}: {}'.format(ex.__class__.__name__, ex), fg='red')


@dialogflow.command(name='pull')
def pull_agent():
    '''Pull agent from Dialogflow Server to local'''
    try:
        lib_cli = lib.Cli()
        lib_cli.pull_agent()
        credential = lib_cli.get_credential("dialogflow")
        click.secho('Pulled agent to: {}'.format(credential['agent_id']))
    except exc.CliException as ex:
        click.secho('{}: {}'.format(ex.__class__.__name__, ex), fg='red')

def main():
    cli()
