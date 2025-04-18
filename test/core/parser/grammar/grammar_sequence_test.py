"""Tests for the Sequence grammar.

NOTE: All of these tests depend somewhat on the KeywordSegment working as planned.
"""

import logging

import pytest

from sqlfluff.core.errors import SQLParseError
from sqlfluff.core.parser import Dedent, Indent, KeywordSegment, StringParser
from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.grammar import Bracketed, Conditional, Sequence
from sqlfluff.core.parser.match_result import MatchResult
from sqlfluff.core.parser.types import ParseMode


def test__parser__grammar_sequence_repr():
    """Test the Sequence grammar __repr__ method."""
    bar = StringParser("bar", KeywordSegment)
    assert repr(bar) == "<StringParser: 'BAR'>"
    foo = StringParser("foo", KeywordSegment)
    sequence = Sequence(bar, foo)
    assert (
        repr(sequence) == "<Sequence: [<StringParser: 'BAR'>, <StringParser: 'FOO'>]>"
    )


def test__parser__grammar_sequence_nested_match(test_segments, caplog):
    """Test the Sequence grammar when nested."""
    bar = StringParser("bar", KeywordSegment)
    foo = StringParser("foo", KeywordSegment)
    baar = StringParser("baar", KeywordSegment)
    g = Sequence(Sequence(bar, foo), baar)

    ctx = ParseContext(dialect=None)
    # Confirm the structure of the test segments:
    assert [s.raw for s in test_segments] == ["bar", " \t ", "foo", "baar", " \t ", ""]

    with caplog.at_level(logging.DEBUG, logger="sqlfluff.parser"):
        # Matching just the start of the list shouldn't work.
        result1 = g.match(test_segments[:3], 0, ctx)

    assert not result1  # Check it returns falsy

    with caplog.at_level(logging.DEBUG, logger="sqlfluff.parser"):
        # Matching the whole list should.
        result2 = g.match(test_segments, 0, ctx)

    assert result2  # Check it returns truthy
    assert result2 == MatchResult(
        matched_slice=slice(0, 4),  # NOTE: One of these is space.
        child_matches=(
            MatchResult(
                matched_slice=slice(0, 1),
                matched_class=KeywordSegment,
                segment_kwargs={"instance_types": ("keyword",)},
            ),
            MatchResult(
                matched_slice=slice(2, 3),
                matched_class=KeywordSegment,
                segment_kwargs={"instance_types": ("keyword",)},
            ),
            MatchResult(
                matched_slice=slice(3, 4),
                matched_class=KeywordSegment,
                segment_kwargs={"instance_types": ("keyword",)},
            ),
        ),
    )


@pytest.mark.parametrize(
    "mode,sequence,terminators,input_slice,output_tuple",
    [
        # #####
        # Test matches where we should get something, and that's
        # the whole sequence.
        # NOTE: Include a little whitespace in the slice (i.e. the first _two_
        # segments) to check that it isn't included in the match.
        (ParseMode.STRICT, ["a"], [], slice(None, 2), (("keyword", "a"),)),
        (ParseMode.GREEDY, ["a"], [], slice(None, 2), (("keyword", "a"),)),
        (ParseMode.GREEDY_ONCE_STARTED, ["a"], [], slice(None, 2), (("keyword", "a"),)),
        # #####
        # Test matching on sequences where we run out of segments before matching
        # the whole sequence.
        # STRICT returns no match.
        (ParseMode.STRICT, ["a", "b"], [], slice(None, 2), ()),
        # GREEDY & GREEDY_ONCE_STARTED returns the content as unparsable, and
        # still don't include the trailing whitespace. The return value does
        # however have the matched "a" as a keyword and not a raw.
        (
            ParseMode.GREEDY,
            ["a", "b"],
            [],
            slice(None, 2),
            (("unparsable", (("keyword", "a"),)),),
        ),
        (
            ParseMode.GREEDY_ONCE_STARTED,
            ["a", "b"],
            [],
            slice(None, 2),
            (("unparsable", (("keyword", "a"),)),),
        ),
        # #####
        # Test matching on sequences where we fail to match the first element.
        # STRICT & GREEDY_ONCE_STARTED return no match.
        (ParseMode.STRICT, ["b"], [], slice(None, 2), ()),
        (ParseMode.GREEDY_ONCE_STARTED, ["b"], [], slice(None, 2), ()),
        # GREEDY claims the remaining elements (unmutated) as unparsable, but
        # does not claim any trailing whitespace.
        (
            ParseMode.GREEDY,
            ["b"],
            [],
            slice(None, 2),
            (("unparsable", (("raw", "a"),)),),
        ),
        # #####
        # Test matches where we should match the sequence fully, but there's more
        # to match.
        # First without terminators...
        # STRICT ignores the rest.
        (ParseMode.STRICT, ["a"], [], slice(None, 5), (("keyword", "a"),)),
        # The GREEDY modes claim the rest as unparsable.
        # NOTE: the whitespace in between is _not_ unparsable.
        (
            ParseMode.GREEDY,
            ["a"],
            [],
            slice(None, 5),
            (
                ("keyword", "a"),
                ("whitespace", " "),
                ("unparsable", (("raw", "b"), ("whitespace", " "), ("raw", "c"))),
            ),
        ),
        (
            ParseMode.GREEDY_ONCE_STARTED,
            ["a"],
            [],
            slice(None, 5),
            (
                ("keyword", "a"),
                ("whitespace", " "),
                ("unparsable", (("raw", "b"), ("whitespace", " "), ("raw", "c"))),
            ),
        ),
        # Second *with* terminators.
        # NOTE: The whitespace before the terminator is not included.
        (ParseMode.STRICT, ["a"], ["c"], slice(None, 5), (("keyword", "a"),)),
        (
            ParseMode.GREEDY,
            ["a"],
            ["c"],
            slice(None, 5),
            (("keyword", "a"), ("whitespace", " "), ("unparsable", (("raw", "b"),))),
        ),
        (
            ParseMode.GREEDY_ONCE_STARTED,
            ["a"],
            ["c"],
            slice(None, 5),
            (("keyword", "a"), ("whitespace", " "), ("unparsable", (("raw", "b"),))),
        ),
        # #####
        # Test matches where we match the first element of a sequence but not the
        # second (with terminators)
        (ParseMode.STRICT, ["a", "x"], ["c"], slice(None, 5), ()),
        # NOTE: For GREEDY modes, the matched portion is not included as an "unparsable"
        # only the portion which failed to match. The terminator is not included and
        # the matched portion is still mutated correctly.
        (
            ParseMode.GREEDY,
            ["a", "x"],
            ["c"],
            slice(None, 5),
            (("keyword", "a"), ("whitespace", " "), ("unparsable", (("raw", "b"),))),
        ),
        (
            ParseMode.GREEDY_ONCE_STARTED,
            ["a", "x"],
            ["c"],
            slice(None, 5),
            (("keyword", "a"), ("whitespace", " "), ("unparsable", (("raw", "b"),))),
        ),
        # #####
        # Test competition between sequence elements and terminators.
        # In GREEDY_ONCE_STARTED, the first element is matched before any terminators.
        (
            ParseMode.GREEDY_ONCE_STARTED,
            ["a"],
            ["a"],
            slice(None, 2),
            (("keyword", "a"),),
        ),
        # In GREEDY, the terminator is matched first and so takes precedence.
        (
            ParseMode.GREEDY,
            ["a"],
            ["a"],
            slice(None, 2),
            (),
        ),
        # NOTE: In these last two cases, the "b" isn't included because it acted as
        # a terminator before being considered in the sequence.
        (
            ParseMode.GREEDY_ONCE_STARTED,
            ["a", "b"],
            ["b"],
            slice(None, 3),
            (("unparsable", (("keyword", "a"),)),),
        ),
        (
            ParseMode.GREEDY,
            ["a", "b"],
            ["b"],
            slice(None, 3),
            (("unparsable", (("keyword", "a"),)),),
        ),
    ],
)
def test__parser__grammar_sequence_modes(
    mode,
    sequence,
    terminators,
    input_slice,
    output_tuple,
    structural_parse_mode_test,
):
    """Test the Sequence grammar with various parse modes.

    In particular here we're testing the treatment of unparsable
    sections.
    """
    structural_parse_mode_test(
        ["a", " ", "b", " ", "c", "d", " ", "d"],
        Sequence,
        sequence,
        terminators,
        {},
        mode,
        input_slice,
        output_tuple,
    )


@pytest.mark.parametrize(
    "input_seed,mode,sequence,kwargs,output_tuple",
    [
        # A strict asymmetric bracket shouldn't match
        (["(", "a"], ParseMode.STRICT, ["a"], {}, ()),
        # A sequence that isn't bracketed shouldn't match.
        # Regardless of mode.
        (["a"], ParseMode.STRICT, ["a"], {}, ()),
        (["a"], ParseMode.GREEDY, ["a"], {}, ()),
        # Test potential empty brackets (no whitespace)
        (
            ["(", ")"],
            ParseMode.STRICT,
            [],
            {},
            (
                (
                    "bracketed",
                    (
                        ("start_bracket", "("),
                        ("indent", ""),
                        ("dedent", ""),
                        ("end_bracket", ")"),
                    ),
                ),
            ),
        ),
        (
            ["(", ")"],
            ParseMode.GREEDY,
            [],
            {},
            (
                (
                    "bracketed",
                    (
                        ("start_bracket", "("),
                        ("indent", ""),
                        ("dedent", ""),
                        ("end_bracket", ")"),
                    ),
                ),
            ),
        ),
        # Test potential empty brackets (with whitespace)
        (
            ["(", " ", ")"],
            ParseMode.STRICT,
            [],
            {},
            (
                (
                    "bracketed",
                    (
                        ("start_bracket", "("),
                        ("indent", ""),
                        ("whitespace", " "),
                        ("dedent", ""),
                        ("end_bracket", ")"),
                    ),
                ),
            ),
        ),
        (
            ["(", " ", ")"],
            ParseMode.GREEDY,
            [],
            {},
            (
                (
                    "bracketed",
                    (
                        ("start_bracket", "("),
                        ("indent", ""),
                        ("whitespace", " "),
                        ("dedent", ""),
                        ("end_bracket", ")"),
                    ),
                ),
            ),
        ),
        (
            ["(", " ", ")"],
            ParseMode.STRICT,
            [],
            # Strict matching, without allowing gaps, shouldn't match.
            {"allow_gaps": False},
            (),
        ),
        (
            ["(", " ", ")"],
            ParseMode.GREEDY,
            [],
            # Greedy matching, without allowing gaps, should return unparsable.
            # NOTE: This functionality doesn't get used much.
            {"allow_gaps": False},
            (
                (
                    "bracketed",
                    (
                        ("start_bracket", "("),
                        ("indent", ""),
                        ("unparsable", (("whitespace", " "),)),
                        ("dedent", ""),
                        ("end_bracket", ")"),
                    ),
                ),
            ),
        ),
        # Happy path content match.
        (
            ["(", "a", ")"],
            ParseMode.STRICT,
            ["a"],
            {},
            (
                (
                    "bracketed",
                    (
                        ("start_bracket", "("),
                        ("indent", ""),
                        ("keyword", "a"),
                        ("dedent", ""),
                        ("end_bracket", ")"),
                    ),
                ),
            ),
        ),
        # Content match fails
        (
            ["(", "a", ")"],
            ParseMode.STRICT,
            ["b"],
            {},
            (),
        ),
        (
            ["(", "a", ")"],
            ParseMode.GREEDY,
            ["b"],
            {},
            (
                (
                    "bracketed",
                    (
                        ("start_bracket", "("),
                        ("indent", ""),
                        ("unparsable", (("raw", "a"),)),
                        ("dedent", ""),
                        ("end_bracket", ")"),
                    ),
                ),
            ),
        ),
        # Partial matches (not whole grammar matched)
        (
            ["(", "a", ")"],
            ParseMode.STRICT,
            ["a", "b"],
            {},
            (),
        ),
        (
            ["(", "a", ")"],
            ParseMode.GREEDY,
            ["a", "b"],
            {},
            (
                (
                    "bracketed",
                    (
                        ("start_bracket", "("),
                        ("indent", ""),
                        ("unparsable", (("keyword", "a"),)),
                        ("dedent", ""),
                        ("end_bracket", ")"),
                    ),
                ),
            ),
        ),
        # Partial matches (not whole sequence matched)
        (
            ["(", "a", " ", "b", ")"],
            ParseMode.STRICT,
            ["a"],
            {},
            (),
        ),
        (
            ["(", "a", " ", "b", ")"],
            ParseMode.GREEDY,
            ["a"],
            {},
            (
                (
                    "bracketed",
                    (
                        ("start_bracket", "("),
                        ("indent", ""),
                        ("keyword", "a"),
                        ("whitespace", " "),
                        ("unparsable", (("raw", "b"),)),
                        ("dedent", ""),
                        ("end_bracket", ")"),
                    ),
                ),
            ),
        ),
        # Test an unwrapped path (with square brackets)
        (
            ["[", "a", " ", "b", "]"],
            ParseMode.GREEDY,
            ["a"],
            {"bracket_type": "square"},
            (
                ("start_square_bracket", "["),
                ("indent", ""),
                ("keyword", "a"),
                ("whitespace", " "),
                ("unparsable", (("raw", "b"),)),
                ("dedent", ""),
                ("end_square_bracket", "]"),
            ),
        ),
    ],
)
def test__parser__grammar_bracketed_modes(
    input_seed,
    mode,
    sequence,
    kwargs,
    output_tuple,
    structural_parse_mode_test,
):
    """Test the Bracketed grammar with various parse modes."""
    structural_parse_mode_test(
        input_seed,
        Bracketed,
        sequence,
        [],
        kwargs,
        mode,
        slice(None, None),
        output_tuple,
    )


@pytest.mark.parametrize(
    "input_seed,mode,sequence",
    [
        # Unclosed greedy brackets always raise errors.
        (["(", "a"], ParseMode.GREEDY, ["a"]),
    ],
)
def test__parser__grammar_bracketed_error_modes(
    input_seed,
    mode,
    sequence,
    structural_parse_mode_test,
):
    """Test the Bracketed grammar with various parse modes."""
    with pytest.raises(SQLParseError):
        structural_parse_mode_test(
            input_seed,
            Bracketed,
            sequence,
            [],
            {},
            mode,
            slice(None, None),
            (),
        )


def test__parser__grammar_sequence_indent_conditional_match(test_segments, caplog):
    """Test the Sequence grammar with indents."""
    bar = StringParser("bar", KeywordSegment)
    foo = StringParser("foo", KeywordSegment)
    # We will assume the default config has indented_joins = False.
    # We're testing without explicitly setting the `config_type` because
    # that's the assumed way of using the grammar in practice.
    g = Sequence(
        Dedent,
        Conditional(Indent, indented_joins=False),
        bar,
        Conditional(Indent, indented_joins=True),
        foo,
        Dedent,
    )
    ctx = ParseContext(dialect=None)
    with caplog.at_level(logging.DEBUG, logger="sqlfluff.parser"):
        m = g.match(test_segments, 0, parse_context=ctx)

    assert m == MatchResult(
        matched_slice=slice(0, 3),  # NOTE: One of these is space.
        child_matches=(
            # The two child keywords
            MatchResult(
                matched_slice=slice(0, 1),
                matched_class=KeywordSegment,
                segment_kwargs={"instance_types": ("keyword",)},
            ),
            MatchResult(
                matched_slice=slice(2, 3),
                matched_class=KeywordSegment,
                segment_kwargs={"instance_types": ("keyword",)},
            ),
        ),
        insert_segments=(
            (0, Dedent),  # The starting, unconditional dedent.
            (0, Indent),  # The conditional (activated) Indent.
            # NOTE: There *isn't* the other Indent.
            (3, Dedent),  # The closing unconditional dedent.
            # NOTE: This last one is still included even though it's
            # after the last matched segment.
        ),
    )
