"""Tests for the BaseGrammar and it's methods.

NOTE: All of these tests depend somewhat on the KeywordSegment working as planned.
"""

import pytest

from sqlfluff.core.dialects.base import Dialect
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
    greedy_match,
    next_ex_bracket_match,
    next_match,
    resolve_bracket,
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
def test__parser__utils__next_match(
    matcher_keywords,
    result_slice,
    winning_matcher,
    test_segments,
):
    """Test the `next_match()` method."""
    # Make the string parsers for testing.
    matchers = [StringParser(keyword, KeywordSegment) for keyword in matcher_keywords]
    # Fetch the matching keyword from above (because it will have the same position)
    if winning_matcher:
        winning_matcher = matchers[matcher_keywords.index(winning_matcher)]

    ctx = ParseContext(dialect=None)
    match, matcher = next_match(
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
def test__parser__utils__resolve_bracket(
    raw_segments, result_slice, generate_test_segments
):
    """Test the `resolve_bracket()` method."""
    test_segments = generate_test_segments(raw_segments)
    start_bracket = StringParser("(", SymbolSegment, type="start_bracket")
    end_bracket = StringParser(")", SymbolSegment, type="end_bracket")
    ctx = ParseContext(dialect=None)

    # For this test case we assert that the first segment is the initial match.
    first_match = start_bracket.match(test_segments, 0, ctx)
    assert first_match

    result = resolve_bracket(
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
def test__parser__utils__next_ex_bracket_match(
    raw_segments, target_word, result_slice, generate_test_segments, test_dialect
):
    """Test the `next_ex_bracket_match()` method."""
    test_segments = generate_test_segments(raw_segments)
    start_bracket = StringParser("(", SymbolSegment, type="start_bracket")
    target = StringParser(target_word, KeywordSegment)
    ctx = ParseContext(dialect=test_dialect)

    # For this test case we assert that the first segment is the initial match.
    first_match = start_bracket.match(test_segments, 0, ctx)
    assert first_match

    result, _ = next_ex_bracket_match(
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
def test__parser__utils__greedy_match(
    raw_segments,
    target_words,
    inc_term,
    result_slice,
    generate_test_segments,
    test_dialect,
):
    """Test the `greedy_match()` method."""
    test_segments = generate_test_segments(raw_segments)
    matchers = [StringParser(word, KeywordSegment) for word in target_words]
    ctx = ParseContext(dialect=test_dialect)

    match = greedy_match(
        segments=test_segments,
        idx=0,
        parse_context=ctx,
        matchers=matchers,
        include_terminator=inc_term,
    )

    assert match
    assert match.matched_slice == result_slice
