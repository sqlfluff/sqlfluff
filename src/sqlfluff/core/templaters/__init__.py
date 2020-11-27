"""Templater Code."""

# flake8: noqa: F401

from .base import templater_selector, TemplatedFile

# Although these shouldn't usually be instantiated from here
# we import them to make sure they get registered.
from .base import RawTemplater
from .jinja import JinjaTemplater
from .python import PythonTemplater
from .dbt import DbtTemplater
