#!/usr/bin/env python3

'''Ejemplo de API REST para ADI'''

from setuptools import setup

setup(
    name='restfs',
    version='0.1',
    description=__doc__,
    packages=['restfs_dirs','restfs_auth','restfs_blob','restfs_common','restfs_client'],
)