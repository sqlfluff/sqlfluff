"""Module to handle cached_property version dependent imports."""
import sys

if sys.version_info >= (3, 8):
    from functools import cached_property
else:  # pragma: no cover
    from backports.cached_property import cached_property

__all__ = ("cached_property",)
