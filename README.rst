==========
bothub-cli
==========
---------------------------
CLI tool for deploy chatbot
---------------------------

This package provides command line interface to `BotHub.studio <https://bothub.studio>`__ service.

Installation
============

To install bothub-cli::

  $ pip install bothub-cli

or, if you are not installing in a ``virtualenv``::

  $ sudo pip install bothub-cli

The bothub-cli package works on python2 and 3 both.


Getting Started
===============

Before using bothub-cli, you need to tell it about your `BotHub.studio <https://bothub.studio>`__ credentials::

  $ bothub configure
  Username: myuser
  Password: mysecret

Then it stores access token on ``~/.bothub`` directory.

To start build your new bot::

  $ mkdir mybot
  $ cd mybot
  $ bothub init
  Project name: mybot

Now you have a starter echo bot::

  .
  |-- bothub
  |   |-- bot.py
  |   `-- __init__.py
  |-- bothub.yml
  |-- requirements.txt
  `-- tests

and deploy it::

  $ bothub deploy

You also need to configure channel to use::

  $ bothub channel add telegram <my-api-key>

Usage
=====

::

   Usage: bothub [OPTIONS] COMMAND [ARGS]...

   Bothub is a command line tool that configure, init, and deploy bot codes
   to BotHub.Studio service

   Options:
     --help  Show this message and exit.

   Commands:
     channel    Setup channels of current project
     configure  Setup credentials
     deploy     Deploy project
     init       Initialize project
     ls         List projects
     rm         Delete a project


Setup
-----

Authorize a user and get access token.::

  $ bothub configure


Project management
------------------

Initialize project on current directory. Create a echo chatbot code.::

  $ bothub init

Deploy current project.::

  $ bothub deploy

List of projects.::

  $ bothub ls

Delete a project.::

  $ bothub rm <project_name>

Channel management
------------------

List of channels for current project.::

  $ bothub channel ls

Add a channel for current project.::

  $ bothub channel add <channel> <api_key>

Remove a channel from current project.::

  $ bothub channel rm <channel>


License
=======

Apache License 2.0
