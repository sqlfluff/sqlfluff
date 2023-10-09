"""Test the KeywordSegment class."""

from sqlfluff.core.parser import KeywordSegment, StringParser
from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.match_result import MatchResult


def test__parser__core_keyword(raw_segments):
    """Test the Mystical KeywordSegment."""
    # First make a keyword
    FooKeyword = StringParser("foobar", KeywordSegment, type="bar")
    # Check it looks as expected
    assert FooKeyword.template.upper() == "FOOBAR"
    ctx = ParseContext(dialect=None)
    # Match it against a list and check it doesn't match
    assert not FooKeyword.match(raw_segments, 1, parse_context=ctx)
    # Match it against the final element (returns tuple)
    m = FooKeyword.match(raw_segments, 0, parse_context=ctx)
    assert m
    assert m == MatchResult(
        matched_slice=slice(0, 1),
        matched_class=KeywordSegment,
        segment_kwargs={"instance_types": ("bar",)},
    )
    segments = m.apply(raw_segments)
    assert len(segments) == 1
    segment = segments[0]
    assert segment.class_types == {
        "base",
        "word",
        "keyword",
        "raw",
        "bar",
    }
