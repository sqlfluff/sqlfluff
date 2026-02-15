"""Test components for working with object and table references."""

import pytest

from sqlfluff.core import Linter
from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.rules import reference


@pytest.mark.parametrize(
    "possible_references, targets, result",
    [
        # Empty list of references is always True.
        [[], [("abc",)], True],
        # Simple cases: one reference, one target.
        [[("agent1",)], [("agent1",)], True],
        [[("agent1",)], [("customer",)], False],
        # Multiple references. If any match, good.
        [[("bar",), ("user_id",)], [("bar",)], True],
        [[("foo",), ("user_id",)], [("bar",)], False],
        # Multiple targets. If any reference matches, good.
        [[("table1",)], [("table1",), ("table2",), ("table3",)], True],
        [[("tbl2",)], [("db", "sc", "tbl1")], False],
        [[("tbl2",)], [("db", "sc", "tbl2")], True],
        # Multi-part references and targets. If one tuple is shorter than
        # the other, checks for a suffix match.
        [
            [
                (
                    "rc",
                    "tbl1",
                )
            ],
            [("db", "sc", "tbl1")],
            False,
        ],
        [
            [
                (
                    "sc",
                    "tbl1",
                )
            ],
            [("db", "sc", "tbl1")],
            True,
        ],
        [
            [
                (
                    "cb",
                    "sc",
                    "tbl1",
                )
            ],
            [("db", "sc", "tbl1")],
            False,
        ],
        [
            [
                (
                    "db",
                    "sc",
                    "tbl1",
                )
            ],
            [("db", "sc", "tbl1")],
            True,
        ],
        [[("public", "agent1")], [("agent1",)], True],
        [[("public", "agent1")], [("public",)], False],
    ],
)
def test_object_ref_matches_table(possible_references, targets, result):
    """Test object_ref_matches_table()."""
    assert reference.object_ref_matches_table(possible_references, targets) == result


@pytest.mark.parametrize(
    "dialect_name, expected",
    [
        ("athena", True),
        ("redshift", True),
        ("bigquery", True),
        ("databricks", True),
        ("duckdb", True),
        ("hive", True),
        ("soql", True),
        ("sparksql", True),
        ("ansi", False),
        ("postgres", False),
        ("snowflake", False),
    ],
)
def test_dialect_supports_dot_access(dialect_name, expected):
    """Test dialect_supports_dot_access()."""
    assert reference.dialect_supports_dot_access(load_raw_dialect(dialect_name)) == expected


@pytest.mark.parametrize(
    "dialect_name, expected",
    [
        ("redshift", True),
        ("bigquery", True),
        ("hive", True),
        ("duckdb", False),
        ("ansi", False),
    ],
)
def test_dialect_has_struct_qualification_ambiguity(dialect_name, expected):
    """Test dialect_has_struct_qualification_ambiguity()."""
    assert (
        reference.dialect_has_struct_qualification_ambiguity(
            load_raw_dialect(dialect_name)
        )
        == expected
    )


def _first_reference(sql: str, dialect: str, ref_type: str = "column_reference"):
    """Parse SQL and return first matching reference segment."""
    parsed = Linter(dialect=dialect).parse_string(sql)
    assert parsed.tree
    return next(parsed.tree.recursive_crawl(ref_type))


def test_extract_reference_table_candidates_redshift_ambiguous():
    """Dot-access dialects include leading and table-level candidates in scope."""
    ref = _first_reference("SELECT t1.t2.c FROM t1", dialect="redshift")
    candidates = reference.extract_reference_table_candidates(
        ref,
        load_raw_dialect("redshift"),
        available_tables={"t1", "t2"},
    )
    assert [name for _, name in candidates] == ["T1", "T2"]


def test_extract_reference_table_candidates_ansi_not_dot_access():
    """Non-dot-access dialects only resolve table-level candidates."""
    ref = _first_reference("SELECT t1.t2.c FROM t1", dialect="ansi")
    candidates = reference.extract_reference_table_candidates(
        ref,
        load_raw_dialect("ansi"),
        available_tables={"t1", "t2"},
    )
    assert [name for _, name in candidates] == ["T2"]


def test_extract_reference_table_candidates_table_path():
    """Dotted table paths can resolve to a prior table alias in scope."""
    parsed = Linter(dialect="redshift").parse_string(
        "SELECT 1 FROM source_table LEFT JOIN source_table.payload.items AS item ON TRUE"
    )
    assert parsed.tree
    table_ref = next(
        ref
        for ref in parsed.tree.recursive_crawl("table_reference")
        if "." in ref.raw
    )
    candidates = reference.extract_reference_table_candidates(
        table_ref,
        load_raw_dialect("redshift"),
        available_tables={"source_table", "item"},
    )
    assert [name for _, name in candidates] == ["SOURCE_TABLE"]
