#!/usr/bin/env python
import setuptools
import os


setuptools.setup(
    name='endpoints-proto-datastore',
    version='0.9.0',
    description='Google Cloud Endpoints Proto Datastore Library',
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
    packages=setuptools.find_packages(exclude=['examples*', 'docs*']),
)