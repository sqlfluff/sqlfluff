"""Templater Code."""

from collections.abc import Iterator

# Although these shouldn't usually be instantiated from here
# we import them to make sure they get registered.
from sqlfluff.core.templaters.base import RawFileSlice, RawTemplater, TemplatedFile
from sqlfluff.core.templaters.jinja import JinjaTemplater
from sqlfluff.core.templaters.placeholder import PlaceholderTemplater
from sqlfluff.core.templaters.python import PythonTemplater


def core_templaters() -> Iterator[type[RawTemplater]]:
    """Returns the templater tuples for the core templaters."""
    yield from [
        RawTemplater,
        JinjaTemplater,
        PythonTemplater,
        PlaceholderTemplater,
    ]


__all__ = (
    "RawFileSlice",
    "TemplatedFile",
    "RawTemplater",
    "JinjaTemplater",
    "PythonTemplater",
    "PlaceholderTemplater",
    "core_templaters",
)
