"""Sqlfluff is a SQL linter for humans."""
import sys

# Expose the public API.
from sqlfluff.api import lint, fix, parse, rules, dialects  # noqa: F401

# Check major python version
if sys.version_info[0] < 3:
    raise Exception("Sqlfluff does not support Python 2. Please upgrade to Python 3.")
# Check minor python version
elif sys.version_info[1] < 6:
    raise Exception(
        (
            "Sqlfluff 0.4.0 only supports Python 3.6 and beyond. "
            "Use an earlier version of sqlfluff or a later version of Python"
        )
    )

# Set the version attribute of the library
import pkg_resources
import configparser

# Get the current version
config = configparser.ConfigParser()
config.read([pkg_resources.resource_filename("sqlfluff", "config.ini")])

__version__ = config.get("sqlfluff", "version")
