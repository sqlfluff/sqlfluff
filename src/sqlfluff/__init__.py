"""Sqlfluff is a SQL linter for humans."""
import pkg_resources
import configparser

# Get the current version
config = configparser.ConfigParser()
config.read([pkg_resources.resource_filename('sqlfluff', 'config.ini')])

__version__ = config.get('sqlfluff', 'version')
