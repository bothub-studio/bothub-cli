# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)

import click


@click.group()
def cli():
    '''Bothub is a command line tool that configure, init,
    and deploy bot codes to BotHub.Studio service'''
    pass


@cli.command()
def configure():
    click.echo('configure')


@cli.command()
def init():
    click.echo('init')


@cli.command()
def deploy():
    click.echo('deploy')


def main():
    cli()
