#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

from os import path

HERE = path.abspath(path.dirname(__file__))

with open(path.join(HERE, 'README.rst'), encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

setup(
    name='bothub-cli',
    version='0.1.0',
    description='A CLI tool for bothub.studio service',
    long_description=LONG_DESCRIPTION,
    author='Jeongsoo Park',
    author_email='toracle@gmail.com',
    url='https://github.com/bothub-studio/bothub-cli',
    license="Apache 2.0",
    packages=[
        'bothub_cli'
    ],
    include_package_data=True,
    install_requires=[
        'six',
        'click',
        'requests',
        'pyyaml',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
        'requests-mock',
    ],
    dependency_links=[
    ],
    entry_points={
        'console_scripts': [
            'bothub=bothub_cli.main:main',
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Communications :: Chat',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Utilities'
    ],
    keywords='bothub serverless chatbot framework cli',
)
