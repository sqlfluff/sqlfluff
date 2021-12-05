"""The Test file for The New Parser (Base Segment Classes)."""

import pytest

from sqlfluff.core.parser import (
    PositionMarker,
    RawSegment,
    BaseSegment,
    BaseFileSegment,
)
from sqlfluff.core.templaters import TemplatedFile
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
    assert BaseSegment.class_is_type("base")
    assert not BaseSegment.class_is_type("foo")
    assert not BaseSegment.class_is_type("foo", "bar")
    assert DummySegment.class_is_type("dummy")
    assert DummySegment.class_is_type("base")
    assert DummySegment.class_is_type("base", "foo", "bar")


def test__parser__base_segments_stubs():
    """Test stub methods that have no implementation in base class."""
    template = TemplatedFile.from_string("foobar")
    rs1 = RawSegment("foobar", PositionMarker(slice(0, 6), slice(0, 6), template))
    base_segment = BaseSegment(segments=[rs1])

    with pytest.raises(NotImplementedError):
        base_segment.edit("foo")


def test__parser__base_segments_raw(raw_seg):
    """Test raw segments behave as expected."""
    # Check Segment Return
    assert raw_seg.segments == []
    assert raw_seg.raw == "foobar"
    # Check Formatting and Stringification
    assert str(raw_seg) == repr(raw_seg) == "<CodeSegment: ([L:  1, P:  1]) 'foobar'>"
    assert (
        raw_seg.stringify(ident=1, tabsize=2)
        == "[L:  1, P:  1]      |  raw:                                                        'foobar'\n"
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
    assert str(base_seg) == repr(base_seg) == "<DummySegment: ([L:  1, P:  1])>"
    assert base_seg.stringify(ident=1, tabsize=2) == (
        "[L:  1, P:  1]      |  dummy:\n"
        "[L:  1, P:  1]      |    raw:                                                      'foobar'\n"
        "[L:  1, P:  7]      |    raw:                                                      '.barfoo'\n"
    )


def test__parser__base_segments_raw_compare():
    """Test comparison of raw segments."""
    template = TemplatedFile.from_string("foobar")
    rs1 = RawSegment("foobar", PositionMarker(slice(0, 6), slice(0, 6), template))
    rs2 = RawSegment("foobar", PositionMarker(slice(0, 6), slice(0, 6), template))
    assert rs1 == rs2


def test__parser__base_segments_base_compare():
    """Test comparison of base segments."""
    template = TemplatedFile.from_string("foobar")
    rs1 = RawSegment("foobar", PositionMarker(slice(0, 6), slice(0, 6), template))
    rs2 = RawSegment("foobar", PositionMarker(slice(0, 6), slice(0, 6), template))

    ds1 = DummySegment([rs1])
    ds2 = DummySegment([rs2])
    dsa2 = DummyAuxSegment([rs2])

    # Check for equality
    assert ds1 == ds2
    # Check a different match on the same details are not the same
    assert ds1 != dsa2


def test__parser__base_segments_file(raw_seg_list):
    """Test BaseFileSegment to behave as expected."""
    base_seg = BaseFileSegment(raw_seg_list, fname="/some/dir/file.sql")
    assert base_seg.type == "file"
    assert base_seg.file_path == "/some/dir/file.sql"
    assert base_seg.can_start_end_non_code
    assert base_seg.allow_empty


def test__parser__raw_get_raw_segments(raw_seg_list):
    """Test niche case of calling get_raw_segments on a raw segment."""
    for s in raw_seg_list:
        assert s.get_raw_segments() == [s]
