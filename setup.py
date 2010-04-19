import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

def read_version(fname):
    '''Read version information from the spec file.'''

    for line in open(fname):
        if line.startswith('Version:'):
            return line.split()[-1]

setup(name='check-ganglia',
        version=read_version('check-ganglia.spec'),
        install_requires=[
            'lxml',
            ],
        description='check_ganglia plugin for Nagios',
        author='Lars Kellogg-Stedman',
        author_email='lars@oddbit.com',
        packages=['check_ganglia'],
        scripts=['scripts/check_ganglia',],
        )

