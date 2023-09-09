"""Tests for the BaseGrammar and it's methods.

NOTE: All of these tests depend somewhat on the KeywordSegment working as planned.
"""

import pytest

from sqlfluff.core.errors import SQLParseError
from sqlfluff.core.parser import KeywordSegment, StringParser
from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.match_algorithms import (
    bracket_sensitive_look_ahead_match,
    look_ahead_match,
)

# NB: All of these tests depend somewhat on the KeywordSegment working as planned


def make_result_tuple(result_slice, matcher_keywords, seg_list):
    """Make a comparison tuple for test matching."""
    # No result slice means no match.
    if not result_slice:
        return ()

    return tuple(
        KeywordSegment(elem.raw, pos_marker=elem.pos_marker)
        if elem.raw in matcher_keywords
        else elem
        for elem in seg_list[result_slice]
    )


@pytest.mark.parametrize(
    "seg_list_slice,matcher_keywords,result_slice,winning_matcher,pre_match_slice",
    [
        # Basic version, we should find bar first
        (slice(None, None), ["bar", "foo"], slice(None, 1), "bar", None),
        # Look ahead for foo
        (slice(None, None), ["foo"], slice(2, 3), "foo", slice(None, 2)),
    ],
)
def test__parser__algorithms__look_ahead_match(
    seg_list_slice,
    matcher_keywords,
    result_slice,
    winning_matcher,
    pre_match_slice,
    seg_list,
):
    """Test the look_ahead_match method of the BaseGrammar."""
    # Make the matcher keywords
    matchers = [StringParser(keyword, KeywordSegment) for keyword in matcher_keywords]
    # Fetch the matching keyword from above by index
    winning_matcher = matchers[matcher_keywords.index(winning_matcher)]

    ctx = ParseContext(dialect=None)
    m = look_ahead_match(
        seg_list[seg_list_slice],
        matchers,
        ctx,
    )

    # Check structure of the response.
    assert isinstance(m, tuple)
    assert len(m) == 3
    # Unpack
    result_pre_match, result_match, result_matcher = m

    # Check the right matcher won
    assert result_matcher == winning_matcher

    # Make check tuple for the pre-match section
    if pre_match_slice:
        pre_match_slice = seg_list[pre_match_slice]
    else:
        pre_match_slice = ()
    assert result_pre_match == pre_match_slice

    # Make the check tuple
    expected_result = make_result_tuple(
        result_slice=result_slice,
        matcher_keywords=matcher_keywords,
        seg_list=seg_list,
    )
    assert result_match.matched_segments == expected_result


def test__parser__algorithms__bracket_sensitive_look_ahead_match(
    bracket_seg_list, fresh_ansi_dialect
):
    """Test the bracket_sensitive_look_ahead_match method of the BaseGrammar."""
    bs = StringParser("bar", KeywordSegment)
    fs = StringParser("foo", KeywordSegment)
    # We need a dialect here to do bracket matching
    ctx = ParseContext(dialect=fresh_ansi_dialect)
    # Basic version, we should find bar first
    pre_section, match, matcher = bracket_sensitive_look_ahead_match(
        bracket_seg_list, [fs, bs], ctx
    )
    assert pre_section == ()
    assert matcher == bs
    # NB the middle element is a match object
    assert match.matched_segments == (
        KeywordSegment("bar", bracket_seg_list[0].pos_marker),
    )

    # Look ahead for foo, we should find the one AFTER the brackets, not the
    # on IN the brackets.
    pre_section, match, matcher = bracket_sensitive_look_ahead_match(
        bracket_seg_list, [fs], ctx
    )
    # NB: The bracket segments will have been mutated, so we can't directly compare.
    # Make sure we've got a bracketed section in there.
    assert len(pre_section) == 5
    assert pre_section[2].is_type("bracketed")
    assert len(pre_section[2].segments) == 4
    assert matcher == fs
    # We shouldn't match the whitespace with the keyword
    assert match.matched_segments == (
        KeywordSegment("foo", bracket_seg_list[8].pos_marker),
    )
    # Check that the unmatched segments are nothing.
    assert not match.unmatched_segments


def test__parser__algorithms__bracket_fail_with_open_paren_close_square_mismatch(
    generate_test_segments, fresh_ansi_dialect
):
    """Test bracket_sensitive_look_ahead_match failure case.

    Should fail when the type of a close bracket doesn't match the type of the
    corresponding open bracket, but both are "definite" brackets.
    """
    fs = StringParser("foo", KeywordSegment)
    # We need a dialect here to do bracket matching
    ctx = ParseContext(dialect=fresh_ansi_dialect)
    # Basic version, we should find bar first
    with pytest.raises(SQLParseError) as sql_parse_error:
        bracket_sensitive_look_ahead_match(
            generate_test_segments(
                [
                    "select",
                    " ",
                    "*",
                    " ",
                    "from",
                    "(",
                    "foo",
                    "]",  # Bracket types don't match (parens vs square)
                ]
            ),
            [fs],
            ctx,
        )
    assert sql_parse_error.match("Found unexpected end bracket")


def test__parser__algorithms__bracket_fail_with_unexpected_end_bracket(
    generate_test_segments, fresh_ansi_dialect
):
    """Test bracket_sensitive_look_ahead_match edge case.

    Should fail gracefully and stop matching if we find a trailing unmatched.
    """
    fs = StringParser("foo", KeywordSegment)
    # We need a dialect here to do bracket matching
    ctx = ParseContext(dialect=fresh_ansi_dialect)
    _, match, _ = bracket_sensitive_look_ahead_match(
        generate_test_segments(
            [
                "bar",
                "(",  # This bracket pair should be mutated
                ")",
                " ",
                ")",  # This is the unmatched bracket
                " ",
                "foo",
            ]
        ),
        [fs],
        ctx,
    )
    # Check we don't match (even though there's a foo at the end)
    assert not match
    # Check the first bracket pair have been mutated.
    segs = match.unmatched_segments
    assert segs[1].is_type("bracketed")
    assert segs[1].raw == "()"
    assert len(segs[1].segments) == 2
    # Check the trailing foo hasn't been mutated
    assert segs[5].raw == "foo"
    assert not isinstance(segs[5], KeywordSegment)
