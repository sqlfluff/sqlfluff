
"""Contains SQL Dialects."""

from .dialect_ansi import ansi_dialect
from .dialect_bigquery import bigquery_dialect


def dialect_selector(s):
    """Return a dialect given it's name."""
    s = s or 'ansi'
    lookup = {
        'ansi': ansi_dialect,
        'bigquery': bigquery_dialect
    }
    return lookup[s]
