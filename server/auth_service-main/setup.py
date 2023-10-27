#!/usr/bin/env python3

'''Distribucion de ADI Auth service'''

from setuptools import setup

setup(
    name='adi-auth',
    version='0.1',
    description=__doc__,
    packages=['adiauth'],
    entry_points={
        'console_scripts': [
            'auth_service=adiauth.server:main'
        ]
    }
)