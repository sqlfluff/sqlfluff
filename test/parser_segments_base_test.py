"""The Test file for The New Parser (Base Segment Classes)."""

import pytest

from sqlfluff.parser.markers import FilePositionMarker
from sqlfluff.parser.segments_base import RawSegment, BaseSegment, ParseContext
from sqlfluff.dialects import ansi_dialect


@pytest.fixture(scope="module")
def raw_seg():
    """Construct a raw segment as a fixture."""
    fp = FilePositionMarker.from_fresh().advance_by('abc')
    return RawSegment('foobar', fp)


@pytest.fixture(scope="module")
def raw_seg_list(raw_seg):
    """Construct a list of raw segments as a fixture."""
    return [
        raw_seg,
        RawSegment(
            '.barfoo',
            raw_seg.pos_marker.advance_by(raw_seg.raw)
        )
    ]


class DummySegment(BaseSegment):
    """A dummy segment for testing with no grammar."""
    type = 'dummy'


class DummyAuxSegment(BaseSegment):
    """A different dummy segment for testing with no grammar."""
    type = 'dummy_aux'


def test__parser__base_segments_raw_init():
    """Test initialisation. Other tests just use the fixture."""
    fp = FilePositionMarker.from_fresh()
    RawSegment('foobar', fp)


def test__parser__base_segments_raw(raw_seg):
    """Test raw segments behave as expected."""
    # Check Segment Return
    assert raw_seg.segments == []
    assert raw_seg.raw == 'foobar'
    # Check Formatting and Stringification
    assert str(raw_seg) == repr(raw_seg) == "<RawSegment: ([3](1, 1, 4)) 'foobar'>"
    assert (raw_seg.stringify(ident=1, tabsize=2, pos_idx=20, raw_idx=35)
            == "  RawSegment:       [3](1, 1, 4)   'foobar'\n")
    # Check tuple
    assert raw_seg.to_tuple() == ('raw', ())
    # Check tuple
    assert raw_seg.to_tuple(show_raw=True) == ('raw', 'foobar')


def test__parser__base_segments_base(raw_seg_list):
    """Test base segments behave as expected."""
    base_seg = DummySegment(raw_seg_list)
    context = ParseContext(dialect=ansi_dialect)
    # Check we assume the position correctly
    assert base_seg.pos_marker == raw_seg_list[0].pos_marker
    # Expand and given we don't have a grammar we should get the same thing
    assert base_seg.parse(parse_context=context) == base_seg
    # Check that we correctly reconstruct the raw
    assert base_seg.raw == "foobar.barfoo"
    # Check tuple
    assert base_seg.to_tuple() == (
        'dummy',
        (
            raw_seg_list[0].to_tuple(),
            raw_seg_list[1].to_tuple()
        )
    )
    # Check Formatting and Stringification
    assert str(base_seg) == repr(base_seg) == "<DummySegment: ([3](1, 1, 4))>"
    assert (base_seg.stringify(ident=1, tabsize=2, pos_idx=20, raw_idx=35)
            == ("  DummySegment:     [3](1, 1, 4)\n"
                "    RawSegment:     [3](1, 1, 4)   'foobar'\n"
                "    RawSegment:     [9](1, 1, 10)  '.barfoo'\n"))


def test__parser__base_segments_raw_compare():
    """Test comparison of raw segments."""
    fp1 = FilePositionMarker.from_fresh()
    fp2 = FilePositionMarker.from_fresh()
    rs1 = RawSegment('foobar', fp1)
    rs2 = RawSegment('foobar', fp2)
    assert rs1 == rs2


def test__parser__base_segments_base_compare():
    """Test comparison of base segments."""
    fp1 = FilePositionMarker.from_fresh()
    fp2 = FilePositionMarker.from_fresh()
    rs1 = RawSegment('foobar', fp1)
    rs2 = RawSegment('foobar', fp2)

    ds1 = DummySegment([rs1])
    ds2 = DummySegment([rs2])
    dsa2 = DummyAuxSegment([rs2])

    # Check for equality
    assert ds1 == ds2
    # Check a different match on the same details are not the same
    assert ds1 != dsa2
