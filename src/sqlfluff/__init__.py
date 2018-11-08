""" __init__.py for sqlfluff """

import configparser

# Get the current version
config = configparser.ConfigParser()
config.read_file(open('src/sqlfluff/config.ini'))

__version__ = config.get('sqlfluff', 'version')
