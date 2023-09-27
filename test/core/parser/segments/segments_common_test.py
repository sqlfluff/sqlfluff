"""Test the KeywordSegment class."""

import pytest

from sqlfluff.core.parser import KeywordSegment, StringParser
from sqlfluff.core.parser.context import ParseContext


# NOTE: For legacy reasons we override this fixture for this module
@pytest.fixture(scope="module")
def raw_segments(generate_test_segments):
    """A generic list of raw segments to test against."""
    return generate_test_segments(["bar", "foo", "bar"])


def test__parser__core_keyword(raw_segments):
    """Test the Mystical KeywordSegment."""
    # First make a keyword
    FooKeyword = StringParser("foo", KeywordSegment, type="bar")
    # Check it looks as expected
    assert FooKeyword.template.upper() == "FOO"
    ctx = ParseContext(dialect=None)
    # Match it against a list and check it doesn't match
    assert not FooKeyword.match(raw_segments, parse_context=ctx)
    # Match it against a the first element and check it doesn't match
    assert not FooKeyword.match(raw_segments[0], parse_context=ctx)
    # Match it against a the first element as a list and check it doesn't match
    assert not FooKeyword.match([raw_segments[0]], parse_context=ctx)
    # Match it against the final element (returns tuple)
    m = FooKeyword.match(raw_segments[1], parse_context=ctx)
    assert m
    assert m.matched_segments[0].raw == "foo"
    assert isinstance(m.matched_segments[0], KeywordSegment)
    # Match it against the final element as a list
    assert FooKeyword.match([raw_segments[1]], parse_context=ctx)
    # Match it against a list slice and check it still works
    assert FooKeyword.match(raw_segments[1:], parse_context=ctx)
    # Check that the types work right. Importantly that the "bar"
    # type makes it in.
    assert m.matched_segments[0].class_types == {
        "base",
        "word",
        "keyword",
        "raw",
        "bar",
    }
