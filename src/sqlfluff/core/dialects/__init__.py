"""Contains SQL Dialects.

Note that individual dialects are only imported as needed at runtime.
This avoids circular references.

To enable this, any modules outside of .dialects cannot import dialects
directly. They should import `dialect_selector` and use that to fetch
dialects.

Within .dialects, each dialect is free to depend on other dialects as
required. Any dependent dialects will be loaded as needed.
"""

from typing import NamedTuple, Iterator, Any
from importlib import import_module


# Eventually it would be a good to dynamically discover dialects
# from any module beginning with "dialect_" within this folder.
from sqlfluff.core.dialects.base import Dialect
from sqlfluff.core.errors import SQLFluffUserError

_dialect_lookup = {
    "ansi": ("dialect_ansi", "ansi_dialect"),
    "bigquery": ("dialect_bigquery", "bigquery_dialect"),
    "exasol": ("dialect_exasol", "exasol_dialect"),
    "hive": ("dialect_hive", "hive_dialect"),
    "mysql": ("dialect_mysql", "mysql_dialect"),
    "postgres": ("dialect_postgres", "postgres_dialect"),
    "redshift": ("dialect_redshift", "redshift_dialect"),
    "snowflake": ("dialect_snowflake", "snowflake_dialect"),
    "sqlite": ("dialect_sqlite", "sqlite_dialect"),
    "teradata": ("dialect_teradata", "teradata_dialect"),
    "tsql": ("dialect_tsql", "tsql_dialect"),
    "spark3": ("dialect_spark3", "spark3_dialect"),
}

_legacy_dialects = {
    "exasol_fs": (
        "As of 0.7.0 the 'exasol_fs' dialect has been combined with "
        "the 'exasol' dialect, and is no longer a standalone dialect. "
        "Please use the 'exasol' dialect instead."
    )
}


def load_raw_dialect(label: str, base_module: str = "sqlfluff.dialects") -> Any:
    """Dynamically load a dialect."""
    if label in _legacy_dialects:
        raise SQLFluffUserError(_legacy_dialects[label])
    module, name = _dialect_lookup[label]
    return getattr(import_module(f"{base_module}.{module}"), name)


class DialectTuple(NamedTuple):
    """Dialect Tuple object for describing dialects."""

    label: str
    name: str
    inherits_from: str


def dialect_readout() -> Iterator[DialectTuple]:
    """Generate a readout of available dialects."""
    for dialect_label in sorted(_dialect_lookup):
        dialect = load_raw_dialect(dialect_label)
        yield DialectTuple(
            label=dialect_label,
            name=dialect.name,
            inherits_from=dialect.inherits_from or "nothing",
        )


def dialect_selector(s: str) -> Dialect:
    """Return a dialect given its name."""
    dialect = load_raw_dialect(s or "ansi")
    # Expand any callable references at this point.
    # NOTE: The result of .expand() is a new class.
    return dialect.expand()
