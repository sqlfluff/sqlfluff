"""The Test file for Parsers (Matchable Classes)."""

from sqlfluff.core.parser import (
    KeywordSegment,
    MultiStringParser,
)
from sqlfluff.core.parser.context import RootParseContext


def test__parser__multistringparser__match(generate_test_segments):
    """Test the MultiStringParser matchable."""
    parser = MultiStringParser(["foo", "bar"], KeywordSegment)
    with RootParseContext(dialect=None) as ctx:
        # Check directly
        seg_list = generate_test_segments(["foo", "fo"])
        # Matches when it should
        assert parser.match(seg_list[:1], parse_context=ctx).matched_segments == (
            KeywordSegment("foo", seg_list[0].pos_marker),
        )
        # Doesn't match when it shouldn't
        assert parser.match(seg_list[1:], parse_context=ctx).matched_segments == tuple()


def test__parser__multistringparser__simple():
    """Test the MultiStringParser matchable."""
    parser = MultiStringParser(["foo", "bar"], KeywordSegment)
    with RootParseContext(dialect=None) as ctx:
        assert parser.simple(ctx)
