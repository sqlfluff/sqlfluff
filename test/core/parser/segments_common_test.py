"""The Test file for The New Parser (Marker Classes)."""

import pytest

from sqlfluff.core.parser import (
    FilePositionMarker,
    RawSegment,
    KeywordSegment,
)
from sqlfluff.core.parser.context import RootParseContext
from sqlfluff.core.parser.segments import EphemeralSegment


@pytest.fixture(scope="module")
def raw_seg_list():
    """A generic list of raw segments to test against."""
    return [
        RawSegment("bar", FilePositionMarker.from_fresh()),
        RawSegment("foo", FilePositionMarker.from_fresh().advance_by("bar")),
        RawSegment("bar", FilePositionMarker.from_fresh().advance_by("barfoo")),
    ]


def test__parser__core_keyword(raw_seg_list):
    """Test the Mystical KeywordSegment."""
    # First make a keyword
    FooKeyword = KeywordSegment.make("foo")
    # Check it looks as expected
    assert issubclass(FooKeyword, KeywordSegment)
    assert FooKeyword.__name__ == "FOO_KeywordSegment"
    assert FooKeyword._template == "FOO"
    with RootParseContext(dialect=None) as ctx:
        # Match it against a list and check it doesn't match
        assert not FooKeyword.match(raw_seg_list, parse_context=ctx)
        # Match it against a the first element and check it doesn't match
        assert not FooKeyword.match(raw_seg_list[0], parse_context=ctx)
        # Match it against a the first element as a list and check it doesn't match
        assert not FooKeyword.match([raw_seg_list[0]], parse_context=ctx)
        # Match it against the final element (returns tuple)
        m = FooKeyword.match(raw_seg_list[1], parse_context=ctx)
        assert m
        assert m.matched_segments[0].raw == "foo"
        assert isinstance(m.matched_segments[0], FooKeyword)
        # Match it against the final element as a list
        assert FooKeyword.match([raw_seg_list[1]], parse_context=ctx)
        # Match it against a list slice and check it still works
        assert FooKeyword.match(raw_seg_list[1:], parse_context=ctx)


def test__parser__core_ephemeral_segment(raw_seg_list):
    """Test the Mystical KeywordSegment."""
    # First make a keyword
    BarKeyword = KeywordSegment.make("bar")

    ephemeral_segment = EphemeralSegment.make(
        match_grammar=BarKeyword, parse_grammar=BarKeyword, name="foobar"
    )

    with RootParseContext(dialect=None) as ctx:
        # Test on a slice containing only the first element
        m = ephemeral_segment.match(raw_seg_list[:1], parse_context=ctx)
        assert m
        # Make sure that it matches as an instance of EphemeralSegment
        elem = m.matched_segments[0]
        assert isinstance(elem, ephemeral_segment)
        # Parse it and make sure we don't get an EphemeralSegment back
        res = elem.parse(ctx)
        assert isinstance(res, tuple)
        elem = res[0]
        assert not isinstance(elem, ephemeral_segment)
        assert isinstance(elem, BarKeyword)
