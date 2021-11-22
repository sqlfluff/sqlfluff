#!/usr/bin/env python
"""The script for setting up sqlfluff."""
import configparser
from setuptools import setup

# Get the global config info as currently stated
# (we use the config file to avoid actually loading any python here)
config = configparser.ConfigParser()
config.read(["src/sqlfluff/config.ini"])
version = config.get("sqlfluff", "version")

setup(version=version)
