# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
import click
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
        for project in projects:
            click.secho(project['name'], fg='green')
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
    pass


@channel.command(name='add')
@click.argument('channel')
@click.argument('api_key')
def add_channel(channel, api_key):
    try:
        lib.add_channel(channel, api_key)
    except exc.CliException as ex:
        click.secho('{}: {}'.format(ex.__class__.__name__, ex), fg='red')


@channel.command(name='ls')
def ls_channel():
    try:
        channels = lib.ls_channel()
        click.secho('\n'.join(channels), fg='green')
    except exc.CliException as ex:
        click.secho('{}: {}'.format(ex.__class__.__name__, ex), fg='red')


@channel.command(name='rm')
@click.argument('channel')
def rm_channel(channel):
    try:
        lib.rm_channel(channel)
    except exc.CliException as ex:
        click.secho('{}: {}'.format(ex.__class__.__name__, ex), fg='red')


def main():
    cli()
