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
    parser = StringParser("foo", ExampleSegment, type="test")
    ctx = ParseContext(dialect=None)
    segments = generate_test_segments(["foo", "bar", "foo"])

    result1 = parser.match2(segments, 0, ctx)
    assert result1
    assert result1.matched_slice == slice(0, 1)
    assert result1.matched_class is ExampleSegment
    assert result1.segment_kwargs == {"instance_types": ("test",)}

    result2 = parser.match2(segments, 1, ctx)
    assert not result2

    result3 = parser.match2(segments, 2, ctx)
    assert result3
    assert result3.matched_slice == slice(2, 3)
    assert result3.matched_class is ExampleSegment
    assert result3.segment_kwargs == {"instance_types": ("test",)}


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
    assert parser.match2(segments, 0, parse_context=ctx).apply(segments) == (
        KeywordSegment("foo", segments[0].pos_marker),
    )
    # Doesn't match when it shouldn't
    assert parser.match2(segments, 1, parse_context=ctx).apply(segments) == tuple()


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


def test__parser__typedparser_rematch(generate_test_segments):
    """Test that TypedParser allows rematching.

    Because the TypedParser looks for types and then changes the
    type as a result, there is a risk of preventing rematching.
    This is a problem because we use it when checking that fix edits
    haven't broken the parse tree.

    In this example the TypedParser is looking for a "single_quote"
    type segment, but is due to mutate to an Example segment, which
    inherits directly from `RawSegment`. Unless the TypedParser
    steps in, this would apparently present a rematching issue.
    """
    segments = generate_test_segments(["'foo'"])
    # Check types pre-match
    assert segments[0].class_types == {
        "single_quote",
        "raw",
        "base",
    }
    parser = TypedParser("single_quote", ExampleSegment)
    # Just check that our assumptions about inheritance are right.
    assert not ExampleSegment.class_is_type("single_quote")
    ctx = ParseContext(dialect=None)
    match1 = parser.match2(segments, 0, ctx)
    assert match1
    # Check types post-match 1
    segments1 = match1.apply(segments)
    assert segments1[0].class_types == {
        # Make sure we got the "example" class
        "example",
        # But we *also* get the "single_quote" class.
        "single_quote",
        "raw",
        "base",
    }
    # Do a rematch to check it works.
    match2 = parser.match2(segments1, 0, ctx)
    assert match2
    # Check types post-match 2
    segments2 = match2.apply(segments1)
    assert segments2[0].class_types == {
        # Make sure we got the same classes on the *rematch*.
        # This is the main crux of the test.
        "example",
        "single_quote",
        "raw",
        "base",
    }
