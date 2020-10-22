"""Contains SQL Dialects."""

from .dialect_ansi import ansi_dialect
from .dialect_bigquery import bigquery_dialect
from .dialect_mysql import mysql_dialect
from .dialect_teradata import teradata_dialect
from .dialect_postgres import postgres_dialect
from .dialect_snowflake import snowflake_dialect


_dialect_lookup = {
    "ansi": ansi_dialect,
    "bigquery": bigquery_dialect,
    "mysql": mysql_dialect,
    "teradata": teradata_dialect,
    "postgres": postgres_dialect,
    "snowflake": snowflake_dialect,
}


def dialect_readout():
    """Generate a readout of available dialects."""
    for dialect_label in _dialect_lookup:
        d = _dialect_lookup[dialect_label]
        yield {
            "label": dialect_label,
            "name": d.name,
            "inherits_from": d.inherits_from or "nothing",
        }


def dialect_selector(s):
    """Return a dialect given it's name."""
    s = s or "ansi"
    dialect = _dialect_lookup[s]
    # Expand any callable references at this point.
    dialect.expand()
    return dialect
