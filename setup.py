#!/usr/bin/env python
import setuptools
import os

README_FILENAME = os.path.join(os.path.dirname(__file__), 'README.rst')
LONG_DESCRIPTION = open(README_FILENAME).read()

setuptools.setup(
    name='endpoints-proto-datastore',
    version='0.9.0',
    description='Google Cloud Endpoints Proto Datastore Library',
    long_description=LONG_DESCRIPTION,
    url='https://github.com/GoogleCloudPlatform/endpoints-proto-datastore',
    license='Apache',
    author='Danny Hermes',
    author_email='daniel.j.hermes@gmail.com',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python'
    ],
    packages=setuptools.find_packages(exclude=['examples*', 'docs*']),
)
