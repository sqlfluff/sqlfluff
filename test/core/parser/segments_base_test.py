"""The Test file for The New Parser (Base Segment Classes)."""

import pytest

from sqlfluff.core.parser import (
    FilePositionMarker,
    RawSegment,
    BaseSegment,
)
from sqlfluff.core.parser.context import RootParseContext
from sqlfluff.core.dialects import ansi_dialect


@pytest.fixture(scope="module")
def raw_seg():
    """Construct a raw segment as a fixture."""
    fp = FilePositionMarker().advance_by("abc")
    return RawSegment("foobar", fp)


@pytest.fixture(scope="module")
def raw_seg_list(raw_seg):
    """Construct a list of raw segments as a fixture."""
    return [raw_seg, RawSegment(".barfoo", raw_seg.pos_marker.advance_by(raw_seg.raw))]


class DummySegment(BaseSegment):
    """A dummy segment for testing with no grammar."""

    type = "dummy"


class DummyAuxSegment(BaseSegment):
    """A different dummy segment for testing with no grammar."""

    type = "dummy_aux"


def test__parser__base_segments_raw_init():
    """Test initialisation. Other tests just use the fixture."""
    RawSegment("foobar", FilePositionMarker())


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
    assert str(raw_seg) == repr(raw_seg) == "<RawSegment: ([3](1, 1, 4)) 'foobar'>"
    assert (
        raw_seg.stringify(ident=1, tabsize=2)
        == "[3](1, 1, 4)        |  raw:                                                        'foobar'\n"
    )
    # Check tuple
    assert raw_seg.to_tuple() == ("raw", ())
    # Check tuple
    assert raw_seg.to_tuple(show_raw=True) == ("raw", "foobar")


def test__parser__base_segments_base(raw_seg_list):
    """Test base segments behave as expected."""
    base_seg = DummySegment(raw_seg_list)
    # Check we assume the position correctly
    assert base_seg.pos_marker == raw_seg_list[0].pos_marker
    with RootParseContext(dialect=ansi_dialect) as ctx:
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
    assert str(base_seg) == repr(base_seg) == "<DummySegment: ([3](1, 1, 4))>"
    assert base_seg.stringify(ident=1, tabsize=2) == (
        "[3](1, 1, 4)        |  dummy:\n"
        "[3](1, 1, 4)        |    raw:                                                      'foobar'\n"
        "[9](1, 1, 10)       |    raw:                                                      '.barfoo'\n"
    )


def test__parser__base_segments_raw_compare():
    """Test comparison of raw segments."""
    rs1 = RawSegment("foobar", FilePositionMarker())
    rs2 = RawSegment("foobar", FilePositionMarker())
    assert rs1 == rs2


def test__parser__base_segments_base_compare():
    """Test comparison of base segments."""
    rs1 = RawSegment("foobar", FilePositionMarker())
    rs2 = RawSegment("foobar", FilePositionMarker())

    ds1 = DummySegment([rs1])
    ds2 = DummySegment([rs2])
    dsa2 = DummyAuxSegment([rs2])

    # Check for equality
    assert ds1 == ds2
    # Check a different match on the same details are not the same
    assert ds1 != dsa2
