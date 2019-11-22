
"""Contains SQL Dialects."""

from .dialect_ansi import ansi_dialect


def dialect_selector(s):
    """Return a dialect given it's name."""
    s = s or 'ansi'
    lookup = {
        'ansi': ansi_dialect
    }
    return lookup[s]
