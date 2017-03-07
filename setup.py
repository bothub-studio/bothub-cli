#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup


setup(
    name='bothub-cli',
    version='0.1.0',
    description=u'',
    author='Jeongsoo Park',
    author_email='toracle@gmail.com',
    url='https://github.com/toracle/bothub-cli',
    packages=find_packages(),
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
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities'
    ],
)
