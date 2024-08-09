"""Tests for the segments module."""

import pytest

import sqlfluff.utils.functional.segment_predicates as sp
from sqlfluff.core.linter.linter import Linter
from sqlfluff.core.parser.segments.raw import RawSegment
from sqlfluff.utils.functional import segments

seg1 = RawSegment("s1")
seg2 = RawSegment("s2")
seg3 = RawSegment("s3")
seg4 = RawSegment("s4")


@pytest.mark.parametrize(
    ["lhs", "rhs", "expected"],
    [
        [
            segments.Segments(seg1, seg2),
            segments.Segments(seg3, seg4),
            segments.Segments(seg1, seg2, seg3, seg4),
        ],
        [
            segments.Segments(seg3, seg4),
            segments.Segments(seg1, seg2),
            segments.Segments(seg3, seg4, seg1, seg2),
        ],
        [
            segments.Segments(seg1, seg2),
            [seg3, seg4],
            segments.Segments(seg1, seg2, seg3, seg4),
        ],
        [
            [seg1, seg2],
            segments.Segments(seg3, seg4),
            segments.Segments(seg1, seg2, seg3, seg4),
        ],
    ],
)
def test_segments_add(lhs, rhs, expected):
    """Verify addition of Segments objects with themselves and lists."""
    result = lhs + rhs
    assert isinstance(result, segments.Segments)
    assert result == expected


@pytest.mark.parametrize(
    ["input", "expected"],
    [
        [
            segments.Segments(seg1, seg2),
            True,
        ],
        [
            segments.Segments(seg1, seg3),
            False,
        ],
    ],
)
def test_segments_all(input, expected):
    """Test the "all()" function."""
    assert input.all(lambda s: s.raw[-1] <= "2") == expected


@pytest.mark.parametrize(
    ["input", "expected"],
    [
        [
            segments.Segments(seg1, seg2),
            True,
        ],
        [
            segments.Segments(seg1, seg3),
            True,
        ],
        [
            segments.Segments(seg3),
            False,
        ],
    ],
)
def test_segments_any(input, expected):
    """Test the "any()" function."""
    assert input.any(lambda s: s.raw[-1] <= "2") == expected


def test_segments_reversed():
    """Test the "reversed()" function."""
    assert segments.Segments(seg1, seg2).reversed() == segments.Segments(seg2, seg1)


def test_segments_raw_slices_no_templated_file():
    """Test that raw_slices() fails if TemplatedFile not provided."""
    with pytest.raises(ValueError):
        segments.Segments(seg1).raw_slices


def test_segments_first_no_predicate():
    """Test the "first()" function with no predicate."""
    assert segments.Segments(seg1, seg2).first() == segments.Segments(seg1)


def test_segments_first_with_predicate():
    """Test the "first()" function with a predicate."""
    assert segments.Segments(seg1, seg2).first(sp.is_meta()) == segments.Segments()


def test_segments_last():
    """Test the "last()" function."""
    assert segments.Segments(seg1, seg2).last() == segments.Segments(seg2)


def test_segments_apply():
    """Test the "apply()" function."""
    assert segments.Segments(seg1, seg2).apply(lambda s: s.raw[-1]) == ["1", "2"]


@pytest.mark.parametrize(
    ["function", "expected"],
    [
        [sp.get_type(), ["raw", "raw"]],
        [sp.is_comment(), [False, False]],
        [sp.is_raw(), [True, True]],
    ],
)
def test_segments_apply_functions(function, expected):
    """Test the "apply()" function with the "get_name()" function."""
    assert segments.Segments(seg1, seg2).apply(function) == expected


def test_segment_predicates_and():
    """Test the "and_()" function."""
    assert segments.Segments(seg1, seg2).select(
        select_if=sp.and_(sp.is_raw(), lambda s: s.raw[-1] == "1")
    ) == segments.Segments(seg1)
    assert (
        segments.Segments(seg1, seg2).select(
            select_if=sp.and_(sp.is_raw(), lambda s: s.raw[-1] == "3")
        )
        == segments.Segments()
    )


def test_segments_recursive_crawl():
    """Test the "recursive_crawl()" function."""
    sql = """
    WITH cte AS (
        SELECT * FROM tab_a
    )
    SELECT
        cte.col_a,
        tab_b.col_b
    FROM cte
    INNER JOIN tab_b;
    """
    linter = Linter(dialect="ansi")
    parsed = linter.parse_string(sql)

    functional_tree = segments.Segments(parsed.root_variant().tree)

    assert len(functional_tree.recursive_crawl("common_table_expression")) == 1
    assert len(functional_tree.recursive_crawl("table_reference")) == 3
