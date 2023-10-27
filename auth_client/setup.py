#!/usr/bin/env python3

'''
    ADI Auth client distrubution file
'''

from setuptools import setup


setup(
    name='adiauthcli',
    version='1.0',
    description='Library and tools to access to ADI Auth Service',
    packages=['adiauthcli'],
    install_requires=['requests']
)
