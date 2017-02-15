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
    lib.package()
    lib.upload()
    click.echo('deploy')


def main():
    cli()
