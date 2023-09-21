"""Tests for the BaseGrammar and it's methods.

NOTE: All of these tests depend somewhat on the KeywordSegment working as planned.
"""

import pytest

from sqlfluff.core.dialects.base import Dialect
from sqlfluff.core.errors import SQLParseError
from sqlfluff.core.parser import (
    CodeSegment,
    KeywordSegment,
    StringParser,
    SymbolSegment,
    WhitespaceSegment,
)
from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.lexer import RegexLexer
from sqlfluff.core.parser.match_algorithms import (
    bracket_sensitive_look_ahead_match,
    greedy_match2,
    look_ahead_match,
    next_ex_bracket_match2,
    next_match2,
    resolve_bracket2,
)

# NB: All of these tests depend somewhat on the KeywordSegment working as planned


@pytest.fixture(scope="function")
def test_dialect():
    """A stripped back test dialect for testing brackets."""
    test_dialect = Dialect("test", root_segment_name="FileSegment")
    test_dialect.bracket_sets("bracket_pairs").update(
        [("round", "StartBracketSegment", "EndBracketSegment", True)]
    )
    test_dialect.set_lexer_matchers(
        [
            RegexLexer("whitespace", r"[^\S\r\n]+", WhitespaceSegment),
            RegexLexer(
                "code", r"[0-9a-zA-Z_]+", CodeSegment, segment_kwargs={"type": "code"}
            ),
        ]
    )
    test_dialect.add(
        StartBracketSegment=StringParser("(", SymbolSegment, type="start_bracket"),
        EndBracketSegment=StringParser(")", SymbolSegment, type="end_bracket"),
    )
    # Return the expanded copy.
    return test_dialect.expand()


def make_result_tuple(result_slice, matcher_keywords, test_segments):
    """Make a comparison tuple for test matching."""
    # No result slice means no match.
    if not result_slice:
        return ()

    return tuple(
        KeywordSegment(elem.raw, pos_marker=elem.pos_marker)
        if elem.raw in matcher_keywords
        else elem
        for elem in test_segments[result_slice]
    )


@pytest.mark.parametrize(
    "segment_slice,matcher_keywords,result_slice,winning_matcher,pre_match_slice",
    [
        # Basic version, we should find bar first
        (slice(None, None), ["bar", "foo"], slice(None, 1), "bar", None),
        # Look ahead for foo
        (slice(None, None), ["foo"], slice(2, 3), "foo", slice(None, 2)),
    ],
)
def test__parser__algorithms__look_ahead_match(
    segment_slice,
    matcher_keywords,
    result_slice,
    winning_matcher,
    pre_match_slice,
    test_segments,
):
    """Test the look_ahead_match method of the BaseGrammar."""
    # Make the matcher keywords
    matchers = [StringParser(keyword, KeywordSegment) for keyword in matcher_keywords]
    # Fetch the matching keyword from above by index
    winning_matcher = matchers[matcher_keywords.index(winning_matcher)]

    ctx = ParseContext(dialect=None)
    m = look_ahead_match(
        test_segments[segment_slice],
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
        pre_match_slice = test_segments[pre_match_slice]
    else:
        pre_match_slice = ()
    assert result_pre_match == pre_match_slice

    # Make the check tuple
    expected_result = make_result_tuple(
        result_slice=result_slice,
        matcher_keywords=matcher_keywords,
        test_segments=test_segments,
    )
    assert result_match.matched_segments == expected_result


def test__parser__algorithms__bracket_sensitive_look_ahead_match(
    bracket_segments, fresh_ansi_dialect
):
    """Test the bracket_sensitive_look_ahead_match method of the BaseGrammar."""
    bs = StringParser("bar", KeywordSegment)
    fs = StringParser("foo", KeywordSegment)
    # We need a dialect here to do bracket matching
    ctx = ParseContext(dialect=fresh_ansi_dialect)
    # Basic version, we should find bar first
    pre_section, match, matcher = bracket_sensitive_look_ahead_match(
        bracket_segments, [fs, bs], ctx
    )
    assert pre_section == ()
    assert matcher == bs
    # NB the middle element is a match object
    assert match.matched_segments == (
        KeywordSegment("bar", bracket_segments[0].pos_marker),
    )

    # Look ahead for foo, we should find the one AFTER the brackets, not the
    # on IN the brackets.
    pre_section, match, matcher = bracket_sensitive_look_ahead_match(
        bracket_segments, [fs], ctx
    )
    # NB: The bracket segments will have been mutated, so we can't directly compare.
    # Make sure we've got a bracketed section in there.
    assert len(pre_section) == 5
    assert pre_section[2].is_type("bracketed")
    assert len(pre_section[2].segments) == 4
    assert matcher == fs
    # We shouldn't match the whitespace with the keyword
    assert match.matched_segments == (
        KeywordSegment("foo", bracket_segments[8].pos_marker),
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
def test__parser__utils__next_match2(
    matcher_keywords,
    result_slice,
    winning_matcher,
    test_segments,
):
    """Test the `next_match2()` method."""
    # Make the string parsers for testing.
    matchers = [StringParser(keyword, KeywordSegment) for keyword in matcher_keywords]
    # Fetch the matching keyword from above (because it will have the same position)
    if winning_matcher:
        winning_matcher = matchers[matcher_keywords.index(winning_matcher)]

    ctx = ParseContext(dialect=None)
    match, matcher = next_match2(
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


@pytest.mark.parametrize(
    "raw_segments,result_slice",
    [
        (["(", "a", ")", " ", "foo"], slice(0, 3)),
        (["(", "a", "(", "b", ")", "(", "c", ")", "d", ")", "e"], slice(0, 10)),
    ],
)
def test__parser__utils__resolve_bracket2(
    raw_segments, result_slice, generate_test_segments
):
    """Test the `resolve_bracket2()` method."""
    test_segments = generate_test_segments(raw_segments)
    start_bracket = StringParser("(", SymbolSegment, type="start_bracket")
    end_bracket = StringParser(")", SymbolSegment, type="end_bracket")
    ctx = ParseContext(dialect=None)

    # For this test case we assert that the first segment is the initial match.
    first_match = start_bracket.match2(test_segments, 0, ctx)
    assert first_match

    result = resolve_bracket2(
        test_segments,
        opening_match=first_match,
        opening_matcher=start_bracket,
        start_brackets=[start_bracket],
        end_brackets=[end_bracket],
        parse_context=ctx,
    )

    assert result
    assert result.matched_slice == result_slice


@pytest.mark.parametrize(
    "raw_segments,target_word,result_slice",
    [
        (["(", "foo", ")", " ", "foo"], "foo", slice(4, 5)),
    ],
)
def test__parser__utils__next_ex_bracket_match2(
    raw_segments, target_word, result_slice, generate_test_segments, test_dialect
):
    """Test the `next_ex_bracket_match2()` method."""
    test_segments = generate_test_segments(raw_segments)
    start_bracket = StringParser("(", SymbolSegment, type="start_bracket")
    target = StringParser(target_word, KeywordSegment)
    ctx = ParseContext(dialect=test_dialect)

    # For this test case we assert that the first segment is the initial match.
    first_match = start_bracket.match2(test_segments, 0, ctx)
    assert first_match

    result, _ = next_ex_bracket_match2(
        test_segments,
        0,
        matchers=[target],
        parse_context=ctx,
    )

    assert result
    assert result.matched_slice == result_slice


@pytest.mark.parametrize(
    "raw_segments,target_words,inc_term,result_slice",
    [
        (["a", "b", " ", "c", "d", " ", "e"], ["e", "c"], False, slice(0, 2)),
        (["a", "b", " ", "c", "d", " ", "e"], ["e", "c"], True, slice(0, 4)),
        # NOTE: Because "b" is_alpha, it needs whitespace before it to match.
        (["a", "b", " ", "b"], ["b"], True, slice(0, 4)),
        (["a", "b", " ", "b"], ["b"], False, slice(0, 2)),
        (["a", "b", "c", " ", "b"], ["b"], False, slice(0, 3)),
    ],
)
def test__parser__utils__greedy_match2(
    raw_segments,
    target_words,
    inc_term,
    result_slice,
    generate_test_segments,
    test_dialect,
):
    """Test the `greedy_match2()` method."""
    test_segments = generate_test_segments(raw_segments)
    matchers = [StringParser(word, KeywordSegment) for word in target_words]
    ctx = ParseContext(dialect=test_dialect)

    match = greedy_match2(
        segments=test_segments,
        idx=0,
        parse_context=ctx,
        matchers=matchers,
        include_terminator=inc_term,
    )

    assert match
    assert match.matched_slice == result_slice
