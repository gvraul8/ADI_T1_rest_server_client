#!/usr/bin/env python3

'''Distribucion de ADI Server service'''

from setuptools import setup

setup(
    name='adi-server',
    version='0.1',
    description=__doc__,
    packages=['adiserver'],
    entry_points={
        'console_scripts': [
            'adi_server=adiserver.server:main'
        ]
    }
)