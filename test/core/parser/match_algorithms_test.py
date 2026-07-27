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
    _next_newline_ex_bracket,
    _next_noncode_ex_bracket,
    greedy_match,
    next_ex_bracket_match,
    next_match,
    resolve_bracket,
    trim_to_terminator,
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
        (
            KeywordSegment(elem.raw, pos_marker=elem.pos_marker)
            if elem.raw in matcher_keywords
            else elem
        )
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
def test__parser__algorithms__next_match(
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

    ctx = ParseContext(dialect=None, max_parse_depth=0)
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
    "raw_segments,result_slice,error",
    [
        (["(", "a", ")", " ", "foo"], slice(0, 3), None),
        (["(", "a", "(", "b", ")", "(", "c", ")", "d", ")", "e"], slice(0, 10), None),
        # This should error because we try to close a square bracket
        # inside a round one.
        (["(", "a", "]", "b", ")", "e"], None, SQLParseError),
        # This should error because we never find the end.
        (["(", "a", " ", "b", " ", "e"], None, SQLParseError),
    ],
)
def test__parser__algorithms__resolve_bracket(
    raw_segments, result_slice, error, generate_test_segments
):
    """Test the `resolve_bracket()` method."""
    test_segments = generate_test_segments(raw_segments)
    start_bracket = StringParser("(", SymbolSegment, type="start_bracket")
    end_bracket = StringParser(")", SymbolSegment, type="end_bracket")
    start_sq_bracket = StringParser("[", SymbolSegment, type="start_square_bracket")
    end_sq_bracket = StringParser("]", SymbolSegment, type="end_square_bracket")
    ctx = ParseContext(dialect=None, max_parse_depth=0)

    # For this test case we assert that the first segment is the initial match.
    first_match = start_bracket.match(test_segments, 0, ctx)
    assert first_match

    args = (test_segments,)
    kwargs = dict(
        opening_match=first_match,
        opening_matcher=start_bracket,
        start_brackets=[start_bracket, start_sq_bracket],
        end_brackets=[end_bracket, end_sq_bracket],
        bracket_persists=[True, False],
        parse_context=ctx,
    )
    # If an error is defined, check that it is raised.
    if error:
        with pytest.raises(error):
            resolve_bracket(*args, **kwargs)
    else:
        result = resolve_bracket(*args, **kwargs)
        assert result
        assert result.matched_slice == result_slice


@pytest.mark.parametrize(
    "raw_segments,target_word,result_slice",
    [
        ([], "foo", slice(0, 0)),
        (["(", "foo", ")", " ", "foo"], "foo", slice(4, 5)),
        (["a", " ", "foo", " ", "foo"], "foo", slice(2, 3)),
        (["foo", " ", "foo", " ", "foo"], "foo", slice(0, 1)),
        # Error case, unexpected closing bracket.
        # NOTE: This should never normally happen, but we should
        # be prepared in case it does so that we return appropriately.
        (["a", " ", ")", " ", "foo"], "foo", slice(0, 0)),
    ],
)
def test__parser__algorithms__next_ex_bracket_match(
    raw_segments, target_word, result_slice, generate_test_segments, test_dialect
):
    """Test the `next_ex_bracket_match()` method."""
    test_segments = generate_test_segments(raw_segments)
    target = StringParser(target_word, KeywordSegment)
    ctx = ParseContext(dialect=test_dialect, max_parse_depth=0)

    result, _, _ = next_ex_bracket_match(
        test_segments,
        0,
        matchers=[target],
        parse_context=ctx,
    )

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
def test__parser__algorithms__greedy_match(
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
    ctx = ParseContext(dialect=test_dialect, max_parse_depth=0)

    match = greedy_match(
        segments=test_segments,
        idx=0,
        parse_context=ctx,
        matchers=matchers,
        include_terminator=inc_term,
    )

    assert match
    assert match.matched_slice == result_slice


def test__parser__algorithms__greedy_match_noncode(
    generate_test_segments,
    test_dialect,
):
    """NonCodeMatcher must terminate greedy_match before whitespace/newlines."""
    from sqlfluff.core.parser.grammar.noncode import NonCodeMatcher

    test_segments = generate_test_segments(["a", "b", " ", "c"])
    ctx = ParseContext(dialect=test_dialect, max_parse_depth=0)

    match = greedy_match(
        segments=test_segments,
        idx=0,
        parse_context=ctx,
        matchers=[NonCodeMatcher()],
        include_terminator=False,
    )

    assert match
    # Claim code only; stop before the whitespace terminator.
    assert match.matched_slice == slice(0, 2)


def test__parser__algorithms__greedy_match_newline(
    generate_test_segments,
    test_dialect,
):
    """NewlineMatcher stops on newlines only, not intra-line spaces."""
    from sqlfluff.core.parser.grammar.newline import NewlineMatcher

    test_segments = generate_test_segments(["a", " ", "b", "\n", "c"])
    ctx = ParseContext(dialect=test_dialect, max_parse_depth=0)

    match = greedy_match(
        segments=test_segments,
        idx=0,
        parse_context=ctx,
        matchers=[NewlineMatcher()],
        include_terminator=False,
    )

    assert match
    # Include the spaced tokens; stop before the newline.
    assert match.matched_slice == slice(0, 3)


@pytest.mark.parametrize(
    "raw_segments,idx,expected",
    [
        # Past end of input.
        (["a"], 1, slice(1, 1)),
        # Already on non-code.
        ([" ", "a"], 0, slice(0, 1)),
        # Non-code before a later bracket.
        (["a", " ", "(", "b", ")"], 0, slice(1, 2)),
        # Skip a bracketed span, then stop on non-code.
        (["a", "(", "b", ")", " ", "c"], 0, slice(4, 5)),
        # Unexpected closing bracket -> no match.
        (["a", ")", " ", "c"], 0, slice(0, 0)),
        # No non-code anywhere.
        (["a", "(", "b", ")", "c"], 0, slice(0, 0)),
        # Bracket consumes to EOF -> empty.
        (["a", "(", "b", ")"], 0, slice(0, 0)),
    ],
)
def test__parser__algorithms__next_noncode_ex_bracket(
    raw_segments,
    idx,
    expected,
    generate_test_segments,
    test_dialect,
):
    """Cover bracket-aware NonCode terminator scanning paths."""
    test_segments = generate_test_segments(raw_segments)
    ctx = ParseContext(dialect=test_dialect, max_parse_depth=0)
    match = _next_noncode_ex_bracket(test_segments, idx, parse_context=ctx)
    assert match.matched_slice == expected


@pytest.mark.parametrize(
    "raw_segments,idx,expected",
    [
        (["a"], 1, slice(1, 1)),
        (["\n", "a"], 0, slice(0, 1)),
        # Spaces are not newlines.
        (["a", " ", "b"], 0, slice(0, 0)),
        (["a", " ", "b", "\n", "c"], 0, slice(3, 4)),
        (["a", "(", "b", ")", "\n", "c"], 0, slice(4, 5)),
        (["a", ")", "\n", "c"], 0, slice(0, 0)),
    ],
)
def test__parser__algorithms__next_newline_ex_bracket(
    raw_segments,
    idx,
    expected,
    generate_test_segments,
    test_dialect,
):
    """Cover bracket-aware newline terminator scanning paths."""
    test_segments = generate_test_segments(raw_segments)
    ctx = ParseContext(dialect=test_dialect, max_parse_depth=0)
    match = _next_newline_ex_bracket(test_segments, idx, parse_context=ctx)
    assert match.matched_slice == expected


@pytest.mark.parametrize(
    "raw_segments,target_words,expected_result",
    [
        # Terminators mid sequence.
        (["a", "b", " ", "c", "d", " ", "e"], ["e", "c"], 2),
        # Initial terminators.
        (["a", "b", " ", "c", "d", " ", "e"], ["a", "e"], 0),
        # No terminators.
        (["a", "b", " ", "c", "d", " ", "e"], ["x", "y"], 7),
        # No sequence.
        ([], ["x", "y"], 0),
    ],
)
def test__parser__algorithms__trim_to_terminator(
    raw_segments,
    target_words,
    expected_result,
    generate_test_segments,
    test_dialect,
):
    """Test the `trim_to_terminator()` method."""
    test_segments = generate_test_segments(raw_segments)
    matchers = [StringParser(word, KeywordSegment) for word in target_words]
    ctx = ParseContext(dialect=test_dialect, max_parse_depth=0)

    assert (
        trim_to_terminator(
            segments=test_segments,
            idx=0,
            parse_context=ctx,
            terminators=matchers,
        )
        == expected_result
    )
