==========
bothub-cli
==========
---------------------------
CLI tool for deploy chatbot
---------------------------

This package provides command line interface to `Bothub.studio`_ service.

Installation
============

To install bothub-cli::

  $ pip install bothub-cli

or, if you are not installing in a ``virtualenv``::

  $ sudo pip install bothub-cli

The bothub-cli package works on python2 and 3 both.


Getting Started
===============

Before using bothub-cli, you need to tell it about your `Bothub.studio`_ credentials.

.. code:: bash

   $ bothub configure
   Username: myuser
   Password: mysecret

Then it stores access token on ``~/.bothub`` directory.

To start build a new bot:

.. code:: bash

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

Edit bot.py below for your purpose.

.. code:: python

   # -*- coding: utf-8 -*-
   
   from __future__ import (absolute_import, division, print_function, unicode_literals)
   
   from bothub_client.bot import BaseBot
   
   
   class Bot(BaseBot):
       """Represent a Bot logic which interacts with a user.
   
       BaseBot superclass have methods belows:
   
       * Send message
         * self.send_message(message, user_id=None, channel=None)
       * Data Storage
         * self.set_project_data(data)
         * self.get_project_data()
         * self.set_user_data(data, user_id=None, channel=None)
         * self.get_user_data(user_id=None, channel=None)
   
       When you omit user_id and channel argument, it regarded as a user
       who triggered a bot.
       """
   
       def handle_message(self, event, context):
           self.send_message(event['content'])

and deploy it.

.. code:: bash

   $ bothub deploy

You also need to configure channel to use.

.. code:: bash

   $ bothub channel add telegram --api-key=<my-api-key>

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

Authorize a user and get access token.

.. code:: bash

   $ bothub configure


Project management
------------------

Initialize project on current directory. Create a echo chatbot code.

.. code:: bash

   $ bothub init

Deploy current project.

.. code:: bash

   $ bothub deploy

List of projects.

.. code:: bash

   $ bothub ls

Delete a project.

.. code:: bash

   $ bothub rm <project_name>

Channel management
------------------

List of channels for current project.

.. code:: bash

   $ bothub channel ls

Add a channel for current project.

.. code:: bash

   $ bothub channel add telegram --api-key=<api_key>
   $ bothub channel add facebook --app-id=<app_id> --app-secret=<app_secret> --page-access-token=<page_access_token>

Remove a channel from current project.

.. code:: bash

   $ bothub channel rm <channel>


Resources
=========

* Documentation (TBD)


License
=======

Apache License 2.0

.. _Bothub.studio: https://bothub.studio
