"""The Test file for The New Parser (Base Segment Classes)."""

import pytest

from sqlfluff.core.parser import (
    PositionMarker,
    RawSegment,
    BaseSegment,
)
from sqlfluff.core.parser.context import RootParseContext


@pytest.fixture(scope="module")
def raw_seg_list(generate_test_segments):
    """Construct a list of raw segments as a fixture."""
    return generate_test_segments(["foobar", ".barfoo"])


@pytest.fixture(scope="module")
def raw_seg(raw_seg_list):
    """Construct a raw segment as a fixture."""
    return raw_seg_list[0]


class DummySegment(BaseSegment):
    """A dummy segment for testing with no grammar."""

    type = "dummy"


class DummyAuxSegment(BaseSegment):
    """A different dummy segment for testing with no grammar."""

    type = "dummy_aux"


def test__parser__base_segments_type():
    """Test the .is_type() method."""
    assert BaseSegment.is_type("base")
    assert not BaseSegment.is_type("foo")
    assert not BaseSegment.is_type("foo", "bar")
    assert DummySegment.is_type("dummy")
    assert DummySegment.is_type("base")
    assert DummySegment.is_type("base", "foo", "bar")


def test__parser__base_segments_raw(raw_seg):
    """Test raw segments behave as expected."""
    # Check Segment Return
    assert raw_seg.segments == []
    assert raw_seg.raw == "foobar"
    # Check Formatting and Stringification
    # NOTE: The preceding underscore shouldn't be there
    # but it's added by .make(). Revisit later.
    assert (
        str(raw_seg)
        == repr(raw_seg)
        == "<_RawSegment: ([C:   0, L:  1, P:  1]) 'foobar'>"
    )
    assert (
        raw_seg.stringify(ident=1, tabsize=2)
        == "[C:   0, L:  1, P:  1]|  raw:                                                        'foobar'\n"
    )
    # Check tuple
    assert raw_seg.to_tuple() == ("raw", ())
    # Check tuple
    assert raw_seg.to_tuple(show_raw=True) == ("raw", "foobar")


def test__parser__base_segments_base(raw_seg_list, fresh_ansi_dialect):
    """Test base segments behave as expected."""
    base_seg = DummySegment(raw_seg_list)
    # Check we assume the position correctly
    assert (
        base_seg.pos_marker.start_point_marker()
        == raw_seg_list[0].pos_marker.start_point_marker()
    )
    assert (
        base_seg.pos_marker.end_point_marker()
        == raw_seg_list[-1].pos_marker.end_point_marker()
    )
    with RootParseContext(dialect=fresh_ansi_dialect) as ctx:
        # Expand and given we don't have a grammar we should get the same thing
        assert base_seg.parse(parse_context=ctx) == base_seg
    # Check that we correctly reconstruct the raw
    assert base_seg.raw == "foobar.barfoo"
    # Check tuple
    assert base_seg.to_tuple() == (
        "dummy",
        (raw_seg_list[0].to_tuple(), raw_seg_list[1].to_tuple()),
    )
    # Check Formatting and Stringification
    assert str(base_seg) == repr(base_seg) == "<DummySegment: ([C:   0, L:  1, P:  1])>"
    assert base_seg.stringify(ident=1, tabsize=2) == (
        "[C:   0, L:  1, P:  1]|  dummy:\n"
        "[C:   0, L:  1, P:  1]|    raw:                                                      'foobar'\n"
        "[C:   6, L:  1, P:  7]|    raw:                                                      '.barfoo'\n"
    )


def test__parser__base_segments_raw_compare():
    """Test comparison of raw segments."""
    rs1 = RawSegment("foobar", PositionMarker(slice(0, 6), slice(0, 6), None))
    rs2 = RawSegment("foobar", PositionMarker(slice(0, 6), slice(0, 6), None))
    assert rs1 == rs2


def test__parser__base_segments_base_compare():
    """Test comparison of base segments."""
    rs1 = RawSegment("foobar", PositionMarker(slice(0, 6), slice(0, 6), None))
    rs2 = RawSegment("foobar", PositionMarker(slice(0, 6), slice(0, 6), None))

    ds1 = DummySegment([rs1])
    ds2 = DummySegment([rs2])
    dsa2 = DummyAuxSegment([rs2])

    # Check for equality
    assert ds1 == ds2
    # Check a different match on the same details are not the same
    assert ds1 != dsa2
