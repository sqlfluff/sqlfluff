"""Modules in this directory provide surrogates.

In this case, the "surrogates" are classes that provide a higher-level API for
writing rules than working with the related, lower-level classes.
"""

__all__ = ("Segments",)

from sqlfluff.core.rules.surrogates.segments import Segments
