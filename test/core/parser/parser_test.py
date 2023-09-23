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


def test__parser__repr():
    """Test the __repr__ method of the parsers."""
    # For the string parser note the uppercase template.
    assert repr(StringParser("foo", KeywordSegment)) == "<StringParser: 'FOO'>"
    # NOTE: For MultiStringParser we only test with one element here
    # because for more than one, the order is unpredictable.
    assert (
        repr(MultiStringParser(["a"], KeywordSegment)) == "<MultiStringParser: {'A'}>"
    )
    # For the typed & regex parser it's case sensitive (although lowercase
    # by convention).
    assert repr(TypedParser("foo", KeywordSegment)) == "<TypedParser: 'foo'>"
    assert repr(RegexParser(r"fo|o", KeywordSegment)) == "<RegexParser: 'fo|o'>"


class ExampleSegment(RawSegment):
    """A minimal example segment for testing."""

    type = "example"


def test__parser__typedparser__simple():
    """Test the simple method of TypedParser."""
    parser = TypedParser("single_quote", ExampleSegment)
    ctx = ParseContext(dialect=None)
    assert parser.simple(ctx) == (frozenset(), frozenset(["single_quote"]))


def test__parser__stringparser__simple():
    """Test the simple method of StringParser."""
    parser = StringParser("foo", ExampleSegment)
    ctx = ParseContext(dialect=None)
    assert parser.simple(ctx) == (frozenset(["FOO"]), frozenset())


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


def test__parser__multistringparser__simple():
    """Test the MultiStringParser matchable."""
    parser = MultiStringParser(["foo", "bar"], KeywordSegment)
    ctx = ParseContext(dialect=None)
    assert parser.simple(ctx) == (frozenset(["FOO", "BAR"]), frozenset())
