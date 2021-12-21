"""Sqlfluff is a SQL linter for humans."""
import sys
import pytest

# Expose the public API.
from sqlfluff.api import lint, fix, parse, list_rules, list_dialects

# Import metadata (using importlib_metadata backport for python versions <3.8)
if sys.version_info >= (3, 8):
    from importlib import metadata
else:
    import importlib_metadata as metadata

__all__ = (
    "lint",
    "fix",
    "parse",
    "list_rules",
    "list_dialects",
)

# Get the current version
__version__ = metadata.version("sqlfluff")

# Check major python version
if sys.version_info[0] < 3:
    raise Exception("Sqlfluff does not support Python 2. Please upgrade to Python 3.")
# Check minor python version
elif sys.version_info[1] < 7:
    raise Exception(
        "Sqlfluff %s only supports Python 3.7 and beyond. "
        "Use an earlier version of sqlfluff or a later version of Python" % __version__
    )

# Register helper functions to support variable introspection on failure.
pytest.register_assert_rewrite("sqlfluff.testing")
