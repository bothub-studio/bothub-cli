# -*- coding: utf-8 -*-

from bothub_cli import utils

def test_get_versions():
    with open('fixtures/pypi-versions.txt') as fin:
        content = fin.read()

    assert utils.find_versions(content) == set(['0.1.3', '0.1.4', '0.1.6', '0.1.7'])


def test_get_latest_version():
    versions = set(['0.1.2', '0.1.10', '0.2.1'])
    assert utils.get_latest_version(versions) == '0.2.1'


def test_cmp_versions():
    assert utils.cmp_versions('0.1.1', '0.1.3') == -1
    assert utils.cmp_versions('0.1.10', '0.1.3') == 1
    assert utils.cmp_versions('0.2.10', '0.1.3') == 1
    assert utils.cmp_versions('0.2.10', '1.1.3') == -1
    assert utils.cmp_versions('0.2.10', '0.2.10') == 0
