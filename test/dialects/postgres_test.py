"""Tests specific to the postgres dialect."""

from collections import Counter
from typing import Callable

import pytest
from _pytest.logging import LogCaptureFixture

from sqlfluff.core import FluffConfig, Linter
from sqlfluff.dialects.dialect_postgres_keywords import (
    get_keywords,
    postgres_docs_keywords,
    postgres_nondocs_keywords,
    postgres_pgvector_keywords,
    postgres_postgis_datatype_keywords,
    postgres_postgis_other_keywords,
    priority_keyword_merge,
)


@pytest.mark.parametrize(
    "segment_reference,raw",
    [
        # AT TIME ZONE constructs
        ("SelectClauseElementSegment", "c_column AT TIME ZONE 'UTC'"),
        ("SelectClauseElementSegment", "(c_column AT TIME ZONE 'UTC')::time"),
        (
            "SelectClauseElementSegment",
            "timestamp with time zone '2021-10-01' AT TIME ZONE 'UTC'",
        ),
        # Notnull and Isnull
        ("ExpressionSegment", "c is null"),
        ("ExpressionSegment", "c is not null"),
        ("ExpressionSegment", "c isnull"),
        ("ExpressionSegment", "c notnull"),
        ("SelectClauseElementSegment", "c is null as c_isnull"),
        ("SelectClauseElementSegment", "c is not null as c_notnull"),
        ("SelectClauseElementSegment", "c isnull as c_isnull"),
        ("SelectClauseElementSegment", "c notnull as c_notnull"),
        ("ArrayAccessorSegment", "[2:10]"),
        ("ArrayAccessorSegment", "[:10]"),
        ("ArrayAccessorSegment", "[2:]"),
        ("ArrayAccessorSegment", "[2]"),
    ],
)
def test_dialect_postgres_specific_segment_parses(
    segment_reference: str,
    raw: str,
    caplog: LogCaptureFixture,
    dialect_specific_segment_parses: Callable,
) -> None:
    """Test that specific segments parse as expected.

    NB: We're testing the PARSE function not the MATCH function
    although this will be a recursive parse and so the match
    function of SUBSECTIONS will be tested if present. The match
    function of the parent will not be tested.
    """
    dialect_specific_segment_parses("postgres", segment_reference, raw, caplog)


@pytest.mark.parametrize(
    "raw",
    [
        "SELECT t1.field, EXTRACT(EPOCH FROM t1.sometime) AS myepoch FROM t1",
        "SELECT t1.field, EXTRACT(EPOCH FROM t1.sometime - t1.othertime) AS myepoch "
        "FROM t1",
    ],
)
def test_epoch_datetime_unit(raw: str) -> None:
    """Test the EPOCH keyword for postgres dialect."""
    # Don't test for new lines or capitalisation
    cfg = FluffConfig(
        configs={"core": {"exclude_rules": "LT12,LT05,LT09", "dialect": "postgres"}}
    )
    lnt = Linter(config=cfg)
    result = lnt.lint_string(raw)
    assert result.num_violations() == 0


@pytest.mark.parametrize(
    "raw",
    [
        "SELECT foo AS space FROM t1",
        "SELECT space.something FROM t1 AS space",
    ],
)
def test_space_is_not_reserved(raw: str) -> None:
    """Ensure that SPACE is not treated as reserved."""
    cfg = FluffConfig(
        configs={"core": {"exclude_rules": "LT12,LT05,AL07", "dialect": "postgres"}}
    )
    lnt = Linter(config=cfg)
    result = lnt.lint_string(raw)
    assert result.num_violations() == 0


@pytest.mark.parametrize(
    "raw",
    [
        # Built-in types must still parse.
        "CREATE TABLE t (a int, b varchar(10), c timestamp, d numeric(5, 2))",
        # DEC and NCHAR / NATIONAL CHARACTER are col_name_keywords that are also
        # real built-in types, so they must still parse (see issue #6430 review).
        "CREATE TABLE t (a dec, b dec(10, 2))",
        "CREATE TABLE t (a nchar(5), b national character(5), c national char)",
        # And their VARYING spellings.
        "CREATE TABLE t (a nchar varying(5), b national character varying(5),"
        " c national char varying(5))",
        # User-defined / unreserved type names must still parse.
        "CREATE TABLE t (x my_custom_type)",
        # `col_name_keyword`s that double as built-in types are still handled by
        # the explicit DatatypeSegment branches.
        "CREATE TABLE t (a bigint, b boolean, c json)",
    ],
)
def test_valid_column_types_parse(raw: str) -> None:
    """Valid column data types parse without unparsable sections."""
    lnt = Linter(dialect="postgres")
    parsed = lnt.parse_string(raw)
    assert not any(True for _ in parsed.tree.recursive_crawl("unparsable"))


@pytest.mark.parametrize(
    "raw",
    [
        # `between` is a col_name_keyword (cannot-be-function-or-type); it must
        # NOT be accepted as a bare data type. See issue #6430. A few
        # representative members of the class are checked since the exclusion is
        # class-wide and the mechanism is shared.
        "CREATE TABLE test_table (type between NOT NULL)",
        "CREATE TABLE test_table (a values)",
        "CREATE TABLE test_table (a setof)",
        "CREATE TABLE test_table (a row)",
    ],
)
def test_col_name_keyword_not_valid_datatype(raw: str) -> None:
    """A `cannot-be-function-or-type` keyword is rejected as a data type."""
    lnt = Linter(dialect="postgres")
    parsed = lnt.parse_string(raw)
    # The invalid type name should produce an unparsable section.
    assert any(True for _ in parsed.tree.recursive_crawl("unparsable"))


@pytest.mark.parametrize(
    "raw",
    [
        # Greenplum adds its own `col_name_keyword`s (cannot-be-function-or-type)
        # on top of PostgreSQL's, e.g. CUBE, ROLLUP, SETS and MEDIAN. The
        # exclusion is inherited from PostgreSQL and extended per-dialect via the
        # `cannot_be_type_keywords` set, so these must also be rejected as bare
        # data types in Greenplum. See issue #6430.
        "CREATE TABLE t (a cube NOT NULL)",
        "CREATE TABLE t (a rollup NOT NULL)",
        "CREATE TABLE t (a sets NOT NULL)",
        "CREATE TABLE t (a median NOT NULL)",
        # Keywords inherited from PostgreSQL must still be rejected too.
        "CREATE TABLE t (a between NOT NULL)",
    ],
)
def test_greenplum_col_name_keyword_not_valid_datatype(raw: str) -> None:
    """A `cannot-be-function-or-type` keyword (incl. inherited) is rejected in Greenplum."""
    lnt = Linter(dialect="greenplum")
    parsed = lnt.parse_string(raw)
    assert any(True for _ in parsed.tree.recursive_crawl("unparsable"))


@pytest.mark.parametrize(
    "raw",
    [
        # Built-in / user-defined type names must still parse in Greenplum
        # (regression guard for the inherited exclusion).
        "CREATE TABLE t (a int, b varchar(10))",
        "CREATE TABLE t (x my_custom_type)",
    ],
)
def test_greenplum_valid_column_types_parse(raw: str) -> None:
    """Valid Greenplum column data types parse without unparsable sections."""
    lnt = Linter(dialect="greenplum")
    parsed = lnt.parse_string(raw)
    assert not any(True for _ in parsed.tree.recursive_crawl("unparsable"))


def test_priority_keyword_merge() -> None:
    """Test merging on keyword lists works as expected."""
    kw_list_1 = [("A", "not-keyword"), ("B", "non-reserved")]

    kw_list_2 = [("A", "reserved"), ("C", "non-reserved")]

    result = priority_keyword_merge(kw_list_1, kw_list_2)

    expected_result = [("A", "reserved"), ("B", "non-reserved"), ("C", "non-reserved")]

    assert sorted(result) == sorted(expected_result)

    kw_list_1 = [("A", "not-keyword"), ("B", "non-reserved")]

    kw_list_2 = [("A", "reserved"), ("C", "non-reserved")]

    result_2 = priority_keyword_merge(kw_list_2, kw_list_1)

    expected_result_2 = [
        ("A", "not-keyword"),
        ("B", "non-reserved"),
        ("C", "non-reserved"),
    ]

    assert sorted(result_2) == sorted(expected_result_2)

    kw_list_1 = [("A", "not-keyword"), ("B", "non-reserved")]

    kw_list_2 = [("A", "reserved"), ("C", "non-reserved")]

    kw_list_3 = [("B", "reserved")]

    result_3 = priority_keyword_merge(kw_list_2, kw_list_1, kw_list_3)

    expected_result_3 = [("A", "not-keyword"), ("B", "reserved"), ("C", "non-reserved")]

    assert sorted(result_3) == sorted(expected_result_3)

    kw_list_1 = [("A", "not-keyword"), ("B", "non-reserved")]

    result_4 = priority_keyword_merge(kw_list_1)

    expected_result_4 = kw_list_1

    assert sorted(result_4) == sorted(expected_result_4)


def test_priority_keyword_merge_leaves_its_inputs_alone() -> None:
    """Test that merging doesn't change the lists it was given.

    It used to append every later list into the first one, so after import
    postgres_docs_keywords held all the layers, not just the docs. Postgres has
    several child dialects; one that merges postgres's layers with its own
    must get them as written, and must not change postgres's lists by doing so.
    """
    kw_list_1 = [("A", "not-keyword"), ("B", "non-reserved")]
    kw_list_2 = [("A", "reserved"), ("C", "non-reserved")]

    result = priority_keyword_merge(kw_list_1, kw_list_2)
    single = priority_keyword_merge(kw_list_1)

    assert kw_list_1 == [("A", "not-keyword"), ("B", "non-reserved")]
    assert kw_list_2 == [("A", "reserved"), ("C", "non-reserved")]
    assert result is not kw_list_1
    assert single is not kw_list_1


def test_priority_keyword_merge_keeps_one_entry_per_keyword() -> None:
    """Test that a keyword listed twice ends up once, with its last status.

    The list version could keep a keyword twice with two statuses: when it was
    repeated in the first list, or in a later list that added it. get_keywords()
    would then put it in two sets that contradict each other.
    """
    first = [("A", "not-keyword"), ("A", "non-reserved"), ("B", "reserved")]
    later = [("C", "reserved"), ("C", "non-reserved"), ("B", "non-reserved")]

    assert priority_keyword_merge(first, later) == [
        ("A", "non-reserved"),
        ("C", "non-reserved"),
        ("B", "non-reserved"),
    ]
    assert priority_keyword_merge(first) == [
        ("A", "non-reserved"),
        ("B", "reserved"),
    ]


@pytest.mark.parametrize(
    "keyword_list",
    [
        postgres_docs_keywords,
        postgres_nondocs_keywords,
        postgres_postgis_datatype_keywords,
        postgres_postgis_other_keywords,
        postgres_pgvector_keywords,
    ],
)
def test_postgres_keyword_layers_list_each_keyword_once(
    keyword_list: list[tuple[str, str]],
) -> None:
    """Test that each keyword layer is (keyword, status) pairs, no keyword twice.

    A keyword listed twice in one layer has two statuses there, and the merge
    silently keeps the last; one of the two is a mistake to fix in the layer.
    """
    for entry in keyword_list:
        assert isinstance(entry, tuple) and len(entry) == 2, entry
        assert all(isinstance(part, str) for part in entry), entry
    counts = Counter(keyword for keyword, _ in keyword_list)
    repeated = sorted(keyword for keyword, count in counts.items() if count > 1)
    assert not repeated, f"Listed more than once in this layer: {repeated}"


def test_get_keywords() -> None:
    """Test keyword filtering works as expected."""
    kw_list = [
        ("A", "not-keyword"),
        ("B", "reserved"),
        ("C", "non-reserved"),
        ("D", "not-keyword"),
        ("E", "non-reserved-(cannot-be-function-or-type)"),
    ]

    expected_result = ["A", "D"]

    assert sorted(get_keywords(kw_list, "not-keyword")) == sorted(expected_result)

    expected_result_2 = ["C", "E"]

    assert sorted(get_keywords(kw_list, "non-reserved")) == sorted(expected_result_2)

    expected_result_3 = ["B"]

    assert sorted(get_keywords(kw_list, "reserved")) == sorted(expected_result_3)
