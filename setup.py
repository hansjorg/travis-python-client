#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='travisclient',
    version = '1.0',
    description = 'Python client for Travis CI',
    author = 'Hans Jørgen Hoel',
    author_email = 'hansjorg@gmail.com',
    url = 'https://github.com/hansjorg/travis-python-client',
    py_modules = ['travisclient'],
    install_requires = ['pycrypto'],
)

