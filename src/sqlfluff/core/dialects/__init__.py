"""Contains SQL Dialects."""

from typing import NamedTuple

from sqlfluff.core.dialects.dialect_ansi import ansi_dialect
from sqlfluff.core.dialects.dialect_bigquery import bigquery_dialect
from sqlfluff.core.dialects.dialect_mysql import mysql_dialect
from sqlfluff.core.dialects.dialect_teradata import teradata_dialect
from sqlfluff.core.dialects.dialect_postgres import postgres_dialect
from sqlfluff.core.dialects.dialect_snowflake import snowflake_dialect
from sqlfluff.core.dialects.dialect_exasol import exasol_dialect
from sqlfluff.core.dialects.dialect_exasol_fs import exasol_fs_dialect


_dialect_lookup = {
    "ansi": ansi_dialect,
    "bigquery": bigquery_dialect,
    "mysql": mysql_dialect,
    "teradata": teradata_dialect,
    "postgres": postgres_dialect,
    "snowflake": snowflake_dialect,
    "exasol": exasol_dialect,
    "exasol_fs": exasol_fs_dialect,
}


class DialectTuple(NamedTuple):
    """Dialect Tuple object for describing dialects."""

    label: str
    name: str
    inherits_from: str


def dialect_readout():
    """Generate a readout of available dialects."""
    for dialect_label in _dialect_lookup:
        d = _dialect_lookup[dialect_label]
        yield DialectTuple(
            label=dialect_label,
            name=d.name,
            inherits_from=d.inherits_from or "nothing",
        )


def dialect_selector(s):
    """Return a dialect given its name."""
    s = s or "ansi"
    dialect = _dialect_lookup[s]
    # Expand any callable references at this point.
    dialect.expand()
    return dialect
