"""Tests for the segments module."""
import pytest

from sqlfluff.core.parser.segments.meta import MetaSegment
from sqlfluff.core.parser.segments.raw import RawSegment
from sqlfluff.core.rules.functional import segments

seg1 = RawSegment("s1")
seg2 = RawSegment("s2")
seg3 = RawSegment("s3")
seg4 = RawSegment("s4")


@pytest.mark.parametrize(
    ["lhs", "rhs", "expected"],
    [
        [
            segments.Segments(None, seg1, seg2),
            segments.Segments(None, seg3, seg4),
            segments.Segments(None, seg1, seg2, seg3, seg4),
        ],
        [
            segments.Segments(None, seg3, seg4),
            segments.Segments(None, seg1, seg2),
            segments.Segments(None, seg3, seg4, seg1, seg2),
        ],
        [
            segments.Segments(None, seg1, seg2),
            [seg3, seg4],
            segments.Segments(None, seg1, seg2, seg3, seg4),
        ],
        [
            [seg1, seg2],
            segments.Segments(None, seg3, seg4),
            segments.Segments(None, seg1, seg2, seg3, seg4),
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
            segments.Segments(None, seg1, seg2),
            True,
        ],
        [
            segments.Segments(None, seg1, seg3),
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
            segments.Segments(None, seg1, seg2),
            True,
        ],
        [
            segments.Segments(None, seg1, seg3),
            True,
        ],
        [
            segments.Segments(None, seg3),
            False,
        ],
    ],
)
def test_segments_any(input, expected):
    """Test the "any()" function."""
    assert input.any(lambda s: s.raw[-1] <= "2") == expected


def test_segments_reversed():
    """Test the "reversed()" function."""
    assert segments.Segments(None, seg1, seg2).reversed() == segments.Segments(
        None, seg2, seg1
    )


def test_segments_first():
    """Test the "first()" function."""
    assert segments.Segments(None, seg1, seg2).first() == segments.Segments(None, seg1)


def test_segments_last():
    """Test the "last()" function."""
    assert segments.Segments(None, seg1, seg2).last() == segments.Segments(None, seg2)


def test_segments_apply():
    """Test the "apply()" function."""
    assert segments.Segments(None, seg1, seg2).apply(lambda s: s.raw[-1]) == ["1", "2"]


def test_composite_predicate_type_names():
    """Test _CompositePredicate with strings, i.e. type names."""
    cp_raw = segments._CompositePredicate("raw")
    assert cp_raw(seg1)
    cp_foobar = segments._CompositePredicate("foobar")
    assert not cp_foobar(seg1)


def test_composite_predicate_types():
    """Test _CompositePredicate with segment types, e.g. BaseSegment."""
    cp_raw = segments._CompositePredicate(RawSegment)
    assert cp_raw(seg1)
    cp_meta = segments._CompositePredicate(MetaSegment)
    assert not cp_meta(seg1)
    cp_both = segments._CompositePredicate(MetaSegment, RawSegment)
    assert cp_both(seg1)


def test_composite_predicate_functions():
    """Test _CompositePredicate with function predicates."""
    cp_1_or_3 = segments._CompositePredicate(
        lambda s: s.raw[-1] == "1", lambda s: s.raw[-1] == "3"
    )
    assert cp_1_or_3(seg1)
    assert not cp_1_or_3(seg2)
    assert cp_1_or_3(seg3)
    assert not cp_1_or_3(seg4)
