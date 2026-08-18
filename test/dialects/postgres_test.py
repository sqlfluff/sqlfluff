"""Tests specific to the postgres dialect."""

from typing import Callable

import pytest
from _pytest.logging import LogCaptureFixture

from sqlfluff.core import FluffConfig, Linter
from sqlfluff.dialects.dialect_postgres_keywords import (
    get_keywords,
    get_keywords_exact,
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


def test_get_keywords_exact() -> None:
    """Test that exact keyword filtering does not match on a prefix."""
    kw_list = [
        ("A", "not-keyword"),
        ("B", "reserved"),
        ("C", "non-reserved"),
        ("D", "reserved-(can-be-function-or-type)"),
        ("E", "non-reserved-(cannot-be-function-or-type)"),
    ]

    # The prefix-matching helper lumps the parenthesised variants in.
    assert sorted(get_keywords(kw_list, "reserved")) == ["B", "D"]
    assert sorted(get_keywords(kw_list, "non-reserved")) == ["C", "E"]

    # The exact helper keeps them apart.
    assert get_keywords_exact(kw_list, "reserved") == ["B"]
    assert get_keywords_exact(kw_list, "non-reserved") == ["C"]
    assert get_keywords_exact(kw_list, "reserved-(can-be-function-or-type)") == ["D"]
    assert get_keywords_exact(kw_list, "non-reserved-(cannot-be-function-or-type)") == [
        "E"
    ]


def _postgres_parse_tree(raw: str):
    """Parse a string with the postgres dialect and return the tree."""
    cfg = FluffConfig(configs={"core": {"dialect": "postgres"}})
    parsed = Linter(config=cfg).parse_string(raw)
    assert parsed.tree is not None
    return parsed.tree


@pytest.mark.parametrize(
    "raw",
    [
        # "BETWEEN" is non-reserved but flagged "cannot be function or type
        # name" by the keyword appendix, so it is not a valid bare type.
        "CREATE TABLE test_table (type between NOT NULL);",
        # Strictly reserved keywords are equally invalid there.
        "CREATE TABLE test_table (a select);",
        "CREATE TABLE test_table (a grant);",
    ],
)
def test_keyword_is_not_a_valid_datatype(raw: str) -> None:
    """Keywords which cannot be a type name should not parse as one.

    https://github.com/sqlfluff/sqlfluff/issues/6430
    """
    tree = _postgres_parse_tree(raw)
    assert list(
        tree.recursive_crawl("unparsable")
    ), f"Expected an unparsable section for {raw!r}, but it parsed cleanly."


@pytest.mark.parametrize(
    "raw",
    [
        # Built-in types are matched by explicit grammar, not by the
        # identifier fallback, so they must keep working.
        "CREATE TABLE t (a int, b varchar(10), c numeric(10, 2));",
        "CREATE TABLE t (a timestamp with time zone, b interval, c boolean);",
        "CREATE TABLE t (a double precision, b text[], c json);",
        # "reserved-(can-be-function-or-type)" keywords remain valid types.
        "CREATE TABLE t (a binary);",
        # User-defined types still fall through to the identifier.
        "CREATE TABLE t (a my_custom_type);",
    ],
)
def test_valid_datatypes_still_parse(raw: str) -> None:
    """The tightened type grammar must not reject legitimate types."""
    tree = _postgres_parse_tree(raw)
    unparsable = list(tree.recursive_crawl("unparsable"))
    assert not unparsable, f"{raw!r} unexpectedly failed to parse: {unparsable}"
