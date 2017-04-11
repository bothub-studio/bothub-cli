# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
import click
from terminaltables import AsciiTable as Table

from bothub_cli import lib
from bothub_cli import exceptions as exc


@click.group()
def cli():
    '''Bothub is a command line tool that configure, init,
    and deploy bot codes to BotHub.Studio service'''
    pass


@cli.command()
def configure():
    '''Setup credentials'''
    try:
        click.echo('Please enter your username/password to get auth token')
        username = click.prompt('username')
        password = click.prompt('password', hide_input=True)
        click.secho('Connecting to server...', fg='green')
        lib.authenticate(username, password)
        click.secho('Authorized', fg='green')
    except exc.CliException as ex:
        click.secho('{}: {}'.format(ex.__class__.__name__, ex), fg='red')


@cli.command()
def init():
    '''Initialize project'''
    click.echo('Initialize a new project')
    while True:
        try:
            if os.path.isfile('bothub.yml'):
                raise exc.Duplicated('Project definition file [bothub.yml] is already exists')
            name = click.prompt('Project name')
            click.secho('Creating project...', fg='green')
            lib.init(name)
            click.secho('Created.', fg='green')
            break
        except exc.CliException as ex:
            click.secho('{}: {}'.format(ex.__class__.__name__, ex), fg='red')
            break


@cli.command()
def deploy():
    '''Deploy project'''
    lib.deploy()
    click.secho('Deployed.', fg='green')


@cli.command()
def ls():
    '''List projects'''
    try:
        projects = lib.ls()
        header = ['project']
        data = [header] + projects
        table = Table(data)
        click.secho(table.table)
    except exc.CliException as ex:
        click.secho('{}: {}'.format(ex.__class__.__name__, ex), fg='red')


@cli.command()
@click.argument('name')
def rm(name):
    '''Delete a project'''
    try:
        lib.rm(name)
    except exc.CliException as ex:
        click.secho('{}: {}'.format(ex.__class__.__name__, ex), fg='red')


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
        lib.add_channel(channel, credentials)
    except exc.CliException as ex:
        click.secho('{}: {}'.format(ex.__class__.__name__, ex), fg='red')


@channel.command(name='ls')
@click.option('-l', '--long', count=True)
def ls_channel(long=False):
    '''List channels of current project'''
    try:
        channels = lib.ls_channel(long)
        header = ['channel']
        if long:
            header.append('credentials')
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
        lib.rm_channel(channel)
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


@property.command(name='get')
@click.argument('key')
def get_property(key):
    '''Get value of a property'''
    try:
        result = lib.get_properties(key)
        if isinstance(result, dict):
            print_properties(result)
        else:
            click.echo('{}: {}'.format(key, result))
    except exc.CliException as ex:
        click.secho('{}: {}'.format(ex.__class__.__name__, ex), fg='red')


@property.command(name='set')
@click.argument('key')
@click.argument('value')
def set_property(key, value):
    '''Set value of a property'''
    try:
        lib.set_properties(key, value)
    except exc.CliException as ex:
        click.secho('{}: {}'.format(ex.__class__.__name__, ex), fg='red')


def main():
    cli()
