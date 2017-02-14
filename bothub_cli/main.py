# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)

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
    except exc.CliException as e:
        click.secho('{}: {}'.format(e.__class__.__name__, e), fg='red')


@cli.command()
def init():
    click.echo('init')


@cli.command()
def deploy():
    click.echo('deploy')


def main():
    cli()
