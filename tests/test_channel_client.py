# -*- coding: utf-8 -*-

import sys
from io import StringIO
from bothub_cli.clients import ConsoleChannelClient


def test_console_channel_client():
    old_out = sys.stdout
    sys.stdout = StringIO()
    client = ConsoleChannelClient()
    client.send_message('123456', 'hello')
    out = sys.stdout.getvalue().strip()
    sys.stdout = old_out
    assert out == 'hello'
