import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='check_gmond',
        version='20100411.1',
        install_requires=[
            'lxml',
            ],
        description='check_gmond plugin for Nagios',
        author='Lars Kellogg-Stedman',
        author_email='lars@seas.harvard.edu',
        packages=['check_gmond'],
        scripts=['scripts/check_gmond',],
        )

