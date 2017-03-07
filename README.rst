==========
bothub-cli
==========
---------------------------
CLI tool for deploy chatbot
---------------------------

This package provides command line interface to BotHub.studio service.

Installation
============

To install bothub-cli::

  $ pip install bothub-cli

or, if you are not installing in a ``virtualenv``::

  $ sudo pip install bothub-cli

The bothub-cli package works on python2 and 3 both.


Getting Started
===============

Before using bothub-cli, you need to tell it about your `BotHub.studio <https://bothub.studio>` credentials::

  $ bothub configure
  Username: myuser
  Password: mysecret

Then it stores access token on ~/.bothub directory.

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
