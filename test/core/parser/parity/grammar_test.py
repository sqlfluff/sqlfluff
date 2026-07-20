"""Dialect grammar integrity checks born from the Rust parity audits.

A ``Ref`` to a name the dialect can't resolve raises RuntimeError in Python
the moment the branch is attempted, while the generated Rust tables silently
treat it as Empty - identical SQL then crashes one engine and quietly fails a
branch on the other. An audit found ~600 such refs, at least one in every
currently-registered dialect, tracked in ``_KNOWN_DANGLING_REF_DIALECTS``
below as a strict xfail per dialect. Because every dialect is currently
listed, this guard enforces nothing today; it starts protecting a dialect
the moment its refs are fixed and it's removed from that set. A handful of
SQL-reachable repros are pinned in ``test/fixtures/parity/dangling_refs.yml``.
"""

import pytest


def _iter_grammar(g, seen):
    if id(g) in seen:
        return
    seen.add(id(g))
    yield g
    for attr in ("_elements", "terminators"):
        for child in getattr(g, attr, ()) or ():
            yield from _iter_grammar(child, seen)
    for attr in ("exclude", "delimiter"):
        child = getattr(g, attr, None)
        if child is not None:
            yield from _iter_grammar(child, seen)


def _dangling_refs(dialect_label):
    from sqlfluff.core.dialects import dialect_selector
    from sqlfluff.core.parser import Ref
    from sqlfluff.core.parser.segments import BaseSegment

    dialect = dialect_selector(dialect_label)
    lib = dialect._library
    seen = set()
    missing = set()
    for entry in lib.values():
        grammar = entry
        if isinstance(grammar, type) and issubclass(grammar, BaseSegment):
            grammar = getattr(grammar, "match_grammar", None)
            if grammar is None:
                continue
        for node in _iter_grammar(grammar, seen):
            if node.__class__ is Ref and node._ref not in lib:
                missing.add(node._ref)
    return missing


def _all_dialect_labels():
    from sqlfluff.core.dialects import dialect_readout

    return [r.label for r in dialect_readout()]


# Dialects with a *known*, already-documented dangling ref (pin an SQL-reachable
# repro in test/fixtures/parity/dangling_refs.yml before listing one here).
# Mostly the shared ansi_keywords FORMATS/POLICIES gap, which every dialect
# inherits. Remove a dialect from this set once its dangling ref is resolved -
# the xfail below is strict, so CI will flag it if it starts passing anyway.
_KNOWN_DANGLING_REF_DIALECTS: set = {
    "ansi",
    "athena",
    "bigquery",
    "clickhouse",
    "databricks",
    "db2",
    "doris",
    "duckdb",
    "exasol",
    "flink",
    "greenplum",
    "hive",
    "impala",
    "mariadb",
    "materialize",
    "mysql",
    "oracle",
    "postgres",
    "redshift",
    "snowflake",
    "soql",
    "sparksql",
    "sqlite",
    "starrocks",
    "teradata",
    "trino",
    "tsql",
    "vertica",
}


def _dialect_param(label):
    if label in _KNOWN_DANGLING_REF_DIALECTS:
        return pytest.param(
            label,
            marks=pytest.mark.xfail(
                strict=True,
                reason=(
                    "Known dangling grammar ref; see test/fixtures/parity/"
                    "dangling_refs.yml."
                ),
            ),
        )
    return pytest.param(label)


@pytest.mark.parametrize(
    "dialect_label", [_dialect_param(label) for label in _all_dialect_labels()]
)
def test__dialect__no_dangling_grammar_refs(dialect_label):
    """Every Ref in every dialect's expanded grammar must resolve."""
    assert _dangling_refs(dialect_label) == set()
