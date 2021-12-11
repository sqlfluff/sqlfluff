"""The Test file for The New Parser (Marker Classes)."""

import pytest

from sqlfluff.core.parser import KeywordSegment, StringParser
from sqlfluff.core.parser.context import RootParseContext
from sqlfluff.core.parser.segments import EphemeralSegment


@pytest.fixture(scope="module")
def raw_seg_list(generate_test_segments):
    """A generic list of raw segments to test against."""
    return generate_test_segments(["bar", "foo", "bar"])


def test__parser__core_keyword(raw_seg_list):
    """Test the Mystical KeywordSegment."""
    # First make a keyword
    FooKeyword = StringParser("foo", KeywordSegment)
    # Check it looks as expected
    assert FooKeyword.template.upper() == "FOO"
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
        assert isinstance(m.matched_segments[0], KeywordSegment)
        # Match it against the final element as a list
        assert FooKeyword.match([raw_seg_list[1]], parse_context=ctx)
        # Match it against a list slice and check it still works
        assert FooKeyword.match(raw_seg_list[1:], parse_context=ctx)


def test__parser__core_ephemeral_segment(raw_seg_list):
    """Test the Mystical KeywordSegment."""
    # First make a keyword
    BarKeyword = StringParser("bar", KeywordSegment)

    ephemeral_segment = EphemeralSegment(
        segments=raw_seg_list[:1],
        pos_marker=None,
        parse_grammar=BarKeyword,
        name="foobar",
    )

    with RootParseContext(dialect=None) as ctx:
        # Parse it and make sure we don't get an EphemeralSegment back
        res = ephemeral_segment.parse(ctx)
        assert isinstance(res, tuple)
        elem = res[0]
        assert not isinstance(elem, EphemeralSegment)
        assert isinstance(elem, KeywordSegment)
