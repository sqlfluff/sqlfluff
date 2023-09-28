"""The Test file for Parsers (Matchable Classes)."""

import pytest

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


@pytest.mark.parametrize(
    "new_type",
    [None, "bar"],
)
def test__parser__typedparser_rematch(new_type, generate_test_segments):
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
    pre_match_types = {
        "single_quote",
        "raw",
        "base",
    }
    post_match_types = {
        # Make sure we got the "example" class
        "example",
        # But we *also* get the "single_quote" class.
        # On the second pass this is the main crux of the test.
        "single_quote",
        "raw",
        "base",
    }
    kwargs = {}
    expected_type = "example"
    if new_type:
        post_match_types.add(new_type)
        kwargs = {"type": new_type}
        expected_type = new_type
    print(kwargs)

    segments = generate_test_segments(["'foo'"])
    # Check types pre-match
    assert segments[0].class_types == pre_match_types

    parser = TypedParser("single_quote", ExampleSegment, **kwargs)
    print(parser._instance_types)
    # Just check that our assumptions about inheritance are right.
    assert not ExampleSegment.class_is_type("single_quote")
    ctx = ParseContext(dialect=None)

    match1 = parser.match(segments, ctx)
    assert match1
    # Check types post-match 1
    assert match1.matched_segments[0].class_types == post_match_types
    assert match1.matched_segments[0].get_type() == expected_type
    assert match1.matched_segments[0].to_tuple(show_raw=True) == (
        expected_type,
        "'foo'",
    )

    # Do a rematch to check it works.
    match2 = parser.match(match1.matched_segments, ctx)
    assert match2
    # Check types post-match 2
    assert match2.matched_segments[0].class_types == post_match_types
    assert match2.matched_segments[0].get_type() == expected_type
    assert match2.matched_segments[0].to_tuple(show_raw=True) == (
        expected_type,
        "'foo'",
    )
