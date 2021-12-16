"""Modules in this directory provide surrogates.

In this case, the "surrogates" are classes that provide a higher-level API for
writing rules than working with the related, lower-level classes.
"""
from operator import attrgetter as attrgetter
from typing import Any, Callable

from sqlfluff.core.rules.surrogates.segments import Segments  # noqa: F401


def attr(*attrs: str) -> Callable[[Any], bool]:
    """Returns a function that gets an attribute of an object.

    This function is useful for creating Predicates for use by
    surrogate object methods.
    """
    getter = attrgetter(*attrs)

    def fn(obj: Any) -> bool:
        return bool(getter(obj))

    return fn
