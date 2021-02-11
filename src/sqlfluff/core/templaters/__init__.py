"""Templater Code."""

# flake8: noqa: F401

from src.sqlfluff.core.templaters.base import templater_selector, TemplatedFile

# Although these shouldn't usually be instantiated from here
# we import them to make sure they get registered.
from src.sqlfluff.core.templaters.base import RawTemplater
from src.sqlfluff.core.templaters.jinja import JinjaTemplater
from src.sqlfluff.core.templaters.python import PythonTemplater
from src.sqlfluff.core.templaters.dbt import DbtTemplater
