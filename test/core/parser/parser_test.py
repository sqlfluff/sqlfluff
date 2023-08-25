"""The Test file for Parsers (Matchable Classes)."""

from sqlfluff.core.parser import (
    KeywordSegment,
    MultiStringParser,
    RawSegment,
    RegexParser,
    StringParser,
    TypedParser,
)
from sqlfluff.core.parser.context import ParseContext


class ExampleSegment(RawSegment):
    """A minimal example segment for testing."""

    type = "example"


def test__parser__typedparser__match2(generate_test_segments):
    """Test the match2 method of TypedParser."""
    parser = TypedParser("single_quote", ExampleSegment)
    ctx = ParseContext(dialect=None)
    # NOTE: The second element of the sequence has single quotes
    # and the test fixture will set the type accordingly.
    segments = generate_test_segments(["foo", "'bar'"])

    result1 = parser.match2(segments, 0, ctx)
    assert not result1

    result2 = parser.match2(segments, 1, ctx)
    assert result2
    assert result2.matched_slice == slice(1, 2)
    assert result2.matched_class is ExampleSegment


def test__parser__typedparser__simple():
    """Test the simple method of TypedParser."""
    parser = TypedParser("single_quote", ExampleSegment)
    ctx = ParseContext(dialect=None)
    assert parser.simple(ctx) == (frozenset(), frozenset(["single_quote"]))


def test__parser__stringparser__match2(generate_test_segments):
    """Test the match2 method of StringParser."""
    parser = StringParser("foo", ExampleSegment)
    ctx = ParseContext(dialect=None)
    segments = generate_test_segments(["foo", "bar", "foo"])

    result1 = parser.match2(segments, 0, ctx)
    assert result1
    assert result1.matched_slice == slice(0, 1)
    assert result1.matched_class is ExampleSegment

    result2 = parser.match2(segments, 1, ctx)
    assert not result2

    result3 = parser.match2(segments, 2, ctx)
    assert result3
    assert result3.matched_slice == slice(2, 3)
    assert result3.matched_class is ExampleSegment


def test__parser__stringparser__simple():
    """Test the simple method of StringParser."""
    parser = StringParser("foo", ExampleSegment)
    ctx = ParseContext(dialect=None)
    assert parser.simple(ctx) == (frozenset(["FOO"]), frozenset())


def test__parser__regexparser__match2(generate_test_segments):
    """Test the match2 method of RegexParser."""
    parser = RegexParser(r"b.r", ExampleSegment)
    ctx = ParseContext(dialect=None)
    segments = generate_test_segments(["foo", "bar", "boo"])

    assert not parser.match2(segments, 0, ctx)
    assert not parser.match2(segments, 2, ctx)

    result = parser.match2(segments, 1, ctx)
    assert result
    assert result.matched_slice == slice(1, 2)
    assert result.matched_class is ExampleSegment


def test__parser__regexparser__simple():
    """Test the simple method of RegexParser."""
    parser = RegexParser(r"b.r", ExampleSegment)
    ctx = ParseContext(dialect=None)
    assert parser.simple(ctx) is None


def test__parser__multistringparser__match(generate_test_segments):
    """Test the MultiStringParser matchable."""
    parser = MultiStringParser(["foo", "bar"], KeywordSegment)
    ctx = ParseContext(dialect=None)
    # Check directly
    segments = generate_test_segments(["foo", "fo"])
    # Matches when it should
    assert parser.match(segments[:1], parse_context=ctx).matched_segments == (
        KeywordSegment("foo", segments[0].pos_marker),
    )
    # Doesn't match when it shouldn't
    assert parser.match(segments[1:], parse_context=ctx).matched_segments == tuple()


def test__parser__multistringparser__match2(generate_test_segments):
    """Test the match2 method of MultiStringParser."""
    parser = MultiStringParser(["foo", "bar"], ExampleSegment)
    ctx = ParseContext(dialect=None)
    segments = generate_test_segments(["foo", "fo", "bar", "boo"])

    assert not parser.match2(segments, 1, ctx)
    assert not parser.match2(segments, 3, ctx)

    result1 = parser.match2(segments, 0, ctx)
    assert result1
    assert result1.matched_slice == slice(0, 1)
    assert result1.matched_class is ExampleSegment

    result2 = parser.match2(segments, 2, ctx)
    assert result2
    assert result2.matched_slice == slice(2, 3)
    assert result2.matched_class is ExampleSegment


def test__parser__multistringparser__simple():
    """Test the MultiStringParser matchable."""
    parser = MultiStringParser(["foo", "bar"], KeywordSegment)
    ctx = ParseContext(dialect=None)
    assert parser.simple(ctx) == (frozenset(["FOO", "BAR"]), frozenset())
