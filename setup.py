#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""The script for setting up sqlfluff."""

from __future__ import absolute_import
from __future__ import print_function

import io
import sys

if sys.version_info[0] < 3:
    raise Exception("SQLFluff does not support Python 2. Please upgrade to Python 3.")

import configparser
from os.path import dirname
from os.path import join

from setuptools import find_packages, setup


# Get the global config info as currently stated
# (we use the config file to avoid actually loading any python here)
config = configparser.ConfigParser()
config.read(["src/sqlfluff/config.ini"])
version = config.get("sqlfluff", "version")


def read(*names, **kwargs):
    """Read a file and return the contents as a string."""
    return io.open(
        join(dirname(__file__), *names), encoding=kwargs.get("encoding", "utf8")
    ).read()


setup(
    name="sqlfluff",
    version=version,
    license="MIT License",
    description="Modular SQL Linting for Humans",
    long_description=read("README.md") + "\n\n---\n\n" + read("CHANGELOG.md"),
    # Make sure pypi is expecting markdown!
    long_description_content_type="text/markdown",
    author="Alan Cruickshank",
    author_email="alan@designingoverload.com",
    url="https://github.com/sqlfluff/sqlfluff",
    python_requires=">=3.6",
    keywords=["sqlfluff", "sql", "linter"],
    project_urls={
        "Homepage": "https://www.sqlfluff.com",
        "Documentation": "https://docs.sqlfluff.com",
        "Source": "https://github.com/sqlfluff/sqlfluff",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 4 - Beta",
        # 'Development Status :: 5 - Production/Stable',
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Utilities",
        "Topic :: Software Development :: Quality Assurance",
    ],
    install_requires=[
        # Core
        "click>=7.1",
        "colorama>=0.3",
        "configparser",
        "oyaml",
        "Jinja2",
        # Used for diffcover plugin
        "diff-cover>=2.5.0",
        # Used for performance profiling
        "bench-it",
        # Used for .sqlfluffignore
        "pathspec",
        # Used for finding os-specific application config dirs
        "appdirs",
        # Cached property for performance gains
        "cached-property",
        # dataclasses backport for python 3.6
        "dataclasses",
        # better type hints for older python versions
        "typing_extensions",
    ],
    extras_require={
        "dbt": ["dbt>=0.17"],
        # eg:
        #   'rst': ['docutils>=0.11'],
        #   ':python_version=="2.6"': ['argparse'],
    },
    entry_points={
        "console_scripts": [
            "sqlfluff = sqlfluff.cli.commands:cli",
        ],
        "diff_cover": ["sqlfluff = sqlfluff.diff_quality_plugin"],
        "sqlfluff": ["sqlfluff = sqlfluff.core.plugin.lib"],
    },
)
