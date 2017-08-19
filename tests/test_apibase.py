# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function, unicode_literals)

import jwt
import time
import logging
from datetime import datetime

import pytest

from bothub_cli import exceptions as exc
from bothub_cli.api import ApiBase
from bothub_cli.utils import timestamp
from .testutils import MockTransport
from .testutils import MockResponse


def test_send_request_should_invoke_function():
    transport = MockTransport()
    transport.record('recorded')
    transport.record('recorded2')
    base = ApiBase(transport=transport)
    response = base._send_request(1, 2, 3, kw1=1, kw2=2)
    assert response == 'recorded'
    assert transport.called[0] == ('get', (1, 2, 3), {'kw1': 1, 'kw2': 2})

    response2 = base._send_request(1, 2, 3, kw1=1, kw2=2, method='post')
    assert response2 == 'recorded2'
    assert transport.called[1] == ('post', (1, 2, 3), {'kw1': 1, 'kw2': 2})


def test_check_auth_token_expired_should_passed():
    auth_token = jwt.encode(
        {
            'content': 'message',
            'exp': timestamp()+10
        },
        key='testkey'
    )
    base = ApiBase(auth_token=auth_token)


def test_check_auth_token_expired_should_raise_expired_exception():
    logging.basicConfig(level=logging.DEBUG)
    auth_token = jwt.encode(
        {
            'content': 'message',
            'exp': timestamp()-10
        },
        key='testkey'
    )
    base = ApiBase(auth_token=auth_token)
    with pytest.raises(exc.AuthTokenExpired):
        base._check_auth_token_expired()


def test_gen_url_should_concat_urls():
    base = ApiBase()
    assert base._gen_url('api', 'v2') == 'https://api.bothub.studio/api/api/v2'


def test_gen_url_should_reflect_base_url():
    base = ApiBase(base_url='https://a.com')
    assert base._gen_url('api', 'v2') == 'https://a.com/api/v2'


def test_get_response_cause_should_extract_cause_field():
    base = ApiBase()
    assert base._get_response_cause(MockResponse('')) is None
    assert base._get_response_cause(MockResponse({'cause': 1234})) == 1234


def test_check_auth_token_should_raise_no_credential():
    with pytest.raises(exc.NoCredential):
        base = ApiBase()
        base._check_auth_token()


def test_check_auth_token_should_pass():
    base = ApiBase(auth_token=1234, verify_token_expire=False)
    base._check_auth_token()
    assert True


def test_check_response_should_pass_with_2xx():
    base = ApiBase()
    base._check_response(MockResponse('', status_code=200))
    base._check_response(MockResponse('', status_code=201))


def test_check_response_should_pass_with_3xx():
    base = ApiBase()
    base._check_response(MockResponse('', status_code=300))
    base._check_response(MockResponse('', status_code=301))


def test_check_response_should_raise_exception_with_4xx():
    base = ApiBase()

    with pytest.raises(exc.InvalidCredential):
        base._check_response(MockResponse('', status_code=401))

    with pytest.raises(exc.NotFound):
        base._check_response(MockResponse('', status_code=404))

    with pytest.raises(exc.Duplicated):
        base._check_response(MockResponse('', status_code=409))

    with pytest.raises(exc.CliException):
        base._check_response(MockResponse('', status_code=400))


def test_get_auth_headers_should_returns_bearer_header():
    base = ApiBase(auth_token='testtoken', verify_token_expire=False)
    assert base._get_auth_headers() == {'Authorization': 'Bearer testtoken'}
