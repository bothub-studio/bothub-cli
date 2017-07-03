# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)

import os
import json
import click
from terminaltables import AsciiTable as Table
from json import JSONDecodeError

from bothub_cli import __version__
from bothub_cli import lib
from bothub_cli import exceptions as exc


def print_error(msg):
    click.secho(msg, fg='red')


@click.group(invoke_without_command=True)
@click.option('-V', '--version', is_flag=True, default=False)
@click.pass_context
def cli(ctx, version):
    '''Bothub is a command line tool that configure, init,
    and deploy bot codes to BotHub.Studio service'''
    try:
        lib.check_latest_version()
    except exc.NotLatestVersion as ex:
        click.secho(str(ex), fg='yellow')

    if version:
        click.secho(__version__)
        return

    if ctx.invoked_subcommand is None:
        print(ctx.get_help())


@cli.command()
def configure():
    '''Setup credentials'''
    try:
        click.echo('Please enter your BotHut.Studio login credentials:')
        username = click.prompt('username')
        password = click.prompt('password', hide_input=True)
        click.secho('Connecting to server...', fg='green')
        lib_cli = lib.Cli()
        lib_cli.authenticate(username, password)
        click.secho('Identified. Welcome {}.'.format(username), fg='green')
    except exc.CliException as ex:
        click.secho('{}: {}'.format(ex.__class__.__name__, ex), fg='red')


@cli.command()
def init():
    '''Initialize project'''
    click.echo('Initialize a new project.')
    while True:
        try:
            lib_cli = lib.Cli()
            _name = None
            clone_needed = True
            # if bothub.yml is exist, ask project_id is exists
            # if then, raise Duplicated
            # else, read bothub.yml and use parameters except project_id
            if os.path.isfile('bothub.yml'):
                try:
                    project_id = lib_cli.get_current_project_id()
                    lib_cli.get_project(project_id)
                    raise exc.Duplicated('Project definition file [bothub.yml] is already exists.')
                except exc.NotFound:
                    print_error('bothub.yml is exist but not a valid project. Create the project again.')
                    clone_needed = False

            name = click.prompt('Project name')
            normalized_name = name.strip()
            if not normalized_name:
                continue
            click.secho('Creating project...', fg='green')
            lib_cli.init(normalized_name, '')
            if clone_needed:
                lib_cli.clone(normalized_name)
            click.secho('Project has created.', fg='green')
            break
        except exc.Cancel:
            print_error('Project creation has cancelled.')
            break
        except exc.CliException as ex:
            print_error('{}: {}'.format(ex.__class__.__name__, ex))
            break


@cli.command()
def deploy():
    '''Deploy project'''
    try:
        lib_cli = lib.Cli()
        lib_cli.deploy(console=click.echo)
        click.secho('Project is deployed.', fg='green')
    except exc.CliException as ex:
        click.secho('{}: {}'.format(ex.__class__.__name__, ex), fg='red')


@cli.command()
@click.argument('project-name')
def clone(project_name):
    '''Clone existing project'''
    try:
        lib_cli = lib.Cli()
        lib_cli.clone(project_name)
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


@channel.command(name='add')
@click.argument('channel')
@click.option('--api-key')
@click.option('--app-id')
@click.option('--app-secret')
@click.option('--page-access-token')
def add_channel(channel, api_key, app_id, app_secret, page_access_token):
    '''Add a new channel to current project'''
    try:
        credentials = {}
        add_option_to_dict(credentials, 'api_key', api_key)
        add_option_to_dict(credentials, 'app_id', app_id)
        add_option_to_dict(credentials, 'app_secret', app_secret)
        add_option_to_dict(credentials, 'page_access_token', page_access_token)
        lib_cli = lib.Cli()
        lib_cli.add_channel(channel, credentials)
        click.secho('Added a channel {}'.format(channel))
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
@click.argument('key')
@click.argument('value')
def set_property(key, value):
    '''Set value of a property'''
    try:
        lib_cli = lib.Cli()
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


@nlu.command(name='add')
@click.argument('nlu')
@click.option('--api-key')
def add_nlu(nlu, api_key):
    '''Add a NLU integration'''
    try:
        lib_cli = lib.Cli()
        credentials = {}
        add_option_to_dict(credentials, 'api_key', api_key)
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
        lib_cli = lib.Cli()
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


def main():
    cli()
