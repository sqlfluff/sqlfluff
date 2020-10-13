"""Sqlfluff is a SQL linter for humans."""
import sys

if sys.version_info[0] < 3:
    raise Exception("Sqlfluff does not support Python 2. Please upgrade to Python 3.")

import pkg_resources
import configparser

# Get the current version
config = configparser.ConfigParser()
config.read([pkg_resources.resource_filename("sqlfluff", "config.ini")])

__version__ = config.get("sqlfluff", "version")
