"""Tests for the BaseGrammar and it's methods.

NOTE: All of these tests depend somewhat on the KeywordSegment working as planned.
"""

import pytest

from sqlfluff.core.parser import KeywordSegment, StringParser
from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.grammar.base import BaseGrammar

# NB: All of these tests depend somewhat on the KeywordSegment working as planned


@pytest.mark.parametrize(
    "matcher_keywords,result_slice,winning_matcher",
    [
        # Basic version, we should find bar first
        (["bar", "foo"], slice(0, 1), "bar"),
        # Look ahead for foo
        (["foo"], slice(2, 3), "foo"),
        # Duplicate matchers
        (["foo", "foo"], slice(2, 3), "foo"),
        (["sadkjfhas", "asefaslf"], slice(0, 0), None),
    ],
)
def test__parser__grammar__base__next_match2(
    matcher_keywords,
    result_slice,
    winning_matcher,
    test_segments,
):
    """Test the _look_ahead_match method of the BaseGrammar."""
    # Make the string parsers for testing.
    matchers = [StringParser(keyword, KeywordSegment) for keyword in matcher_keywords]
    # Fetch the matching keyword from above (because it will have the same position)
    if winning_matcher:
        winning_matcher = matchers[matcher_keywords.index(winning_matcher)]

    ctx = ParseContext(dialect=None)
    match, matcher = BaseGrammar._next_match2(
        test_segments,
        0,
        matchers,
        ctx,
    )

    # Check the right matcher was successful.
    if winning_matcher:
        assert matcher is winning_matcher
    else:
        # If no designated winning matcher, assert that it wasn't successful.
        assert matcher is None
        assert not match
    assert match.matched_slice == result_slice
