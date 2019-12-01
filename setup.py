#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""The script for setting up sqlfluff."""

from __future__ import absolute_import
from __future__ import print_function

import io
try:
    import configparser
except ImportError:
    import ConfigParser as configparser
from os.path import dirname
from os.path import join

from setuptools import setup


# Get the global config info as currently stated
# (we use the config file to avoid actually loading any python here)
config = configparser.ConfigParser()
config.read(['src/sqlfluff/config.ini'])
version = config.get('sqlfluff', 'version')


def read(*names, **kwargs):
    """Read a file and return the contents as a string."""
    return io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()


setup(
    name='sqlfluff',
    version=version,
    license='MIT License',
    description='Modular SQL Linting for Humans',
    long_description=read('README.md') + "\n\n---\n\n" + read('CHANGELOG.md'),
    # Make sure pypi is expecting markdown!
    long_description_content_type='text/markdown',
    author='Alan Cruickshank',
    author_email='alan@designingoverload.com',
    url='https://github.com/alanmcruickshank/sqlfluff',
    # Specify all the seperate packages, modules come automatically
    packages=['sqlfluff', 'sqlfluff.cli', 'sqlfluff.dialects', 'sqlfluff.parser', 'sqlfluff.rules'],
    package_dir={"": "src"},
    include_package_data=True,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 3 - Alpha',
        # 'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Utilities',
        'Topic :: Software Development :: Quality Assurance'
    ],
    keywords=[
        # eg: 'keyword1', 'keyword2', 'keyword3',
    ],
    install_requires=[
        'click>=2.0',
        'six>=1.0'
    ],
    extras_require={
        # eg:
        #   'rst': ['docutils>=0.11'],
        #   ':python_version=="2.6"': ['argparse'],
    },
    entry_points={
        'console_scripts': [
            'sqlfluff = sqlfluff.cli.commands:cli',
        ]
    },
    # Use datafiles to make sure the config versioning file is included
    data_files=[('', ['src/sqlfluff/config.ini', 'README.md', 'CHANGELOG.md'])]
)
