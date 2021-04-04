"""Templater Code."""

# flake8: noqa: F401

from sqlfluff.core.templaters.base import templater_selector, TemplatedFile

# Although these shouldn't usually be instantiated from here
# we import them to make sure they get registered.
from sqlfluff.core.templaters.base import RawTemplater
from sqlfluff.core.templaters.jinja import JinjaTemplater
from sqlfluff.core.templaters.python import PythonTemplater
from sqlfluff.core.templaters.dbt import DbtTemplater
