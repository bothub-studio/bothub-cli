# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)

import click
from bothub_cli import lib


@click.group()
def cli():
    '''Bothub is a command line tool that configure, init,
    and deploy bot codes to BotHub.Studio service'''
    pass


@cli.command()
def configure():
    '''Setup credentials'''
    # input id, pw
    # get token
    # save it to file
    click.echo('Please enter your username/password to get auth token')
    username = click.prompt('username')
    password = click.prompt('password')

    lib.authenticate(username, password)
    click.echo('configure')


@cli.command()
def init():
    click.echo('init')


@cli.command()
def deploy():
    click.echo('deploy')


def main():
    cli()
