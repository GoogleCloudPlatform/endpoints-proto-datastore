#!/usr/bin/env python
from setuptools import setup, find_packages
import os


setup(
    ### Metadata
    name='endpoints-proto-datastore',
    version='1.0.0',
    description='Endpoints Proto Datastore API',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.md')).read(),
    url='https://github.com/GoogleCloudPlatform/endpoints-proto-datastore',
    license='Apache',
    author='Danny Hermes',
    author_email='daniel.j.hermes@gmail.com',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python'
    ],
    ### Contents
    packages=find_packages(exclude=['examples*', 'docs*']),
)
