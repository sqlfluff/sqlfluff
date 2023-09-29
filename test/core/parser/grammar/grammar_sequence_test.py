"""Tests for the Sequence grammar.

NOTE: All of these tests depend somewhat on the KeywordSegment working as planned.
"""

import logging

import pytest

from sqlfluff.core.parser import Dedent, Indent, KeywordSegment, StringParser
from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.grammar import Conditional, Sequence
from sqlfluff.core.parser.match_result import MatchResult2
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


def test__parser__grammar_sequence_nested_match2(test_segments, caplog):
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
        result1 = g.match2(test_segments[:3], 0, ctx)

    assert not result1  # Check it returns falsy

    with caplog.at_level(logging.DEBUG, logger="sqlfluff.parser"):
        # Matching the whole list should.
        result2 = g.match2(test_segments, 0, ctx)

    assert result2  # Check it returns truthy
    assert result2 == MatchResult2(
        matched_slice=slice(0, 4),  # NOTE: One of these is space.
        child_matches=(
            MatchResult2(
                matched_slice=slice(0, 1),
                matched_class=KeywordSegment,
                segment_kwargs={"instance_types": ("keyword",)},
            ),
            MatchResult2(
                matched_slice=slice(2, 3),
                matched_class=KeywordSegment,
                segment_kwargs={"instance_types": ("keyword",)},
            ),
            MatchResult2(
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
def test__parser__grammar_sequence_modes2(
    mode,
    sequence,
    terminators,
    input_slice,
    output_tuple,
    generate_test_segments,
    fresh_ansi_dialect,
):
    """Test the Sequence grammar with various parse modes.

    In particular here we're testing the treatment of unparsable
    sections.
    """
    segments = generate_test_segments(["a", " ", "b", " ", "c", "d", " ", "d"])
    # Dialect is required here only to have access to bracket segments.
    ctx = ParseContext(dialect=fresh_ansi_dialect)

    _seq = Sequence(
        *(StringParser(e, KeywordSegment) for e in sequence),
        parse_mode=mode,
        terminators=[StringParser(e, KeywordSegment) for e in terminators]
    )
    _start = input_slice.start or 0
    _stop = input_slice.stop or len(segments)
    _match = _seq.match2(segments[:_stop], _start, ctx)
    # If we're expecting an output tuple, assert the match is truthy.
    if output_tuple:
        assert _match
    _result = tuple(
        e.to_tuple(show_raw=True, code_only=False) for e in _match.apply(segments)
    )
    assert _result == output_tuple


def test__parser__grammar_sequence_indent_conditional_match2(test_segments, caplog):
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
        m = g.match2(test_segments, 0, parse_context=ctx)

    assert m == MatchResult2(
        matched_slice=slice(0, 3),  # NOTE: One of these is space.
        child_matches=(
            # The two child keywords
            MatchResult2(
                matched_slice=slice(0, 1),
                matched_class=KeywordSegment,
                segment_kwargs={"instance_types": ("keyword",)},
            ),
            MatchResult2(
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
