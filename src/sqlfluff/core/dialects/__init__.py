"""Contains SQL Dialects.

Note that individual dialects are only imported as needed at runtime.
This avoids circular references in python 3.6.

To enable this, any modules outside of .dialects cannot import dialects
directly. They should import `dialect_selector` and use that to fetch
dialects.

Within .dialects, each dialect is free to depend on other dialects as
required. Any dependent dialects will be loaded as needed.
"""

from typing import NamedTuple
from importlib import import_module


# Eventually it would be a good to dynamically discover dialects
# from any module beginning with "dialect_" within this folder.
_dialect_lookup = {
    "ansi": ("dialect_ansi", "ansi_dialect"),
    "bigquery": ("dialect_bigquery", "bigquery_dialect"),
    "mysql": ("dialect_mysql", "mysql_dialect"),
    "teradata": ("dialect_teradata", "teradata_dialect"),
    "postgres": ("dialect_postgres", "postgres_dialect"),
    "snowflake": ("dialect_snowflake", "snowflake_dialect"),
    "exasol": ("dialect_exasol", "exasol_dialect"),
    "exasol_fs": ("dialect_exasol_fs", "exasol_fs_dialect"),
    "tsql": ("dialect_tsql", "tsql_dialect"),
}


def load_raw_dialect(label, base_module="sqlfluff.dialects"):
    """Dynamically load a dialect."""
    module, name = _dialect_lookup[label]
    return getattr(import_module(f"{base_module}.{module}"), name)


class DialectTuple(NamedTuple):
    """Dialect Tuple object for describing dialects."""

    label: str
    name: str
    inherits_from: str


def dialect_readout():
    """Generate a readout of available dialects."""
    for dialect_label in sorted(_dialect_lookup):
        dialect = load_raw_dialect(dialect_label)
        yield DialectTuple(
            label=dialect_label,
            name=dialect.name,
            inherits_from=dialect.inherits_from or "nothing",
        )


def dialect_selector(s):
    """Return a dialect given its name."""
    dialect = load_raw_dialect(s or "ansi")
    # Expand any callable references at this point.
    # NOTE: The result of .expand() is a new class.
    return dialect.expand()
