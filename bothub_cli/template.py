# -*- coding: utf-8 -*-

code = '''# -*- coding: utf-8 -*-

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
        """Handle a message received

        event is a dict and contains trigger info.

        {
           "trigger": "webhook",
           "channel": "<name>",
           "sender": {
              "id": "<chat_id>",
              "name": "<nickname>"
           },
           "content": "<message content>",
           "raw_data": <unmodified data itself webhook received>
        }
        """
        self.send_message('Echo: {}'.format(event['content']))
'''
