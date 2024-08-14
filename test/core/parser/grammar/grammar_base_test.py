"""Tests for the BaseGrammar and it's methods.

NOTE: All of these tests depend somewhat on the KeywordSegment working as planned.
"""

import logging

import pytest

from sqlfluff.core.parser import KeywordSegment, StringParser
from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.grammar import OneOf, Sequence
from sqlfluff.core.parser.grammar.base import BaseGrammar
from sqlfluff.core.parser.segments import EphemeralSegment

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
    "seg_list_slice,matcher_keywords,trim_noncode,result_slice",
    [
        # Matching the first element of the list
        (slice(None, None), ["bar"], False, slice(None, 1)),
        # Matching with a bit of whitespace before
        (slice(1, None), ["foo"], True, slice(1, 3)),
        # Matching with a bit of whitespace before (not trim_noncode)
        (slice(1, None), ["foo"], False, None),
        # Matching with whitespace after
        (slice(None, 2), ["bar"], True, slice(None, 2)),
    ],
)
def test__parser__grammar__base__longest_trimmed_match__basic(
    seg_list, seg_list_slice, matcher_keywords, trim_noncode, result_slice
):
    """Test the _longest_trimmed_match method of the BaseGrammar."""
    # Make the matcher keywords
    matchers = [StringParser(keyword, KeywordSegment) for keyword in matcher_keywords]

    ctx = ParseContext(dialect=None)
    m, _ = BaseGrammar._longest_trimmed_match(
        seg_list[seg_list_slice], matchers, ctx, trim_noncode=trim_noncode
    )

    # Make the check tuple
    expected_result = make_result_tuple(
        result_slice=result_slice,
        matcher_keywords=matcher_keywords,
        seg_list=seg_list,
    )

    assert m.matched_segments == expected_result


def test__parser__grammar__base__longest_trimmed_match__adv(seg_list, caplog):
    """Test the _longest_trimmed_match method of the BaseGrammar."""
    bs = StringParser("bar", KeywordSegment)
    fs = StringParser("foo", KeywordSegment)
    matchers = [
        bs,
        fs,
        Sequence(bs, fs),  # This should be the winner.
        OneOf(bs, fs),
        Sequence(bs, fs),  # Another to check we return the first
    ]
    ctx = ParseContext(dialect=None)
    # Matching the first element of the list
    with caplog.at_level(logging.DEBUG, logger="sqluff.parser"):
        match, matcher = BaseGrammar._longest_trimmed_match(seg_list, matchers, ctx)
    # Check we got a match
    assert match
    # Check we got the right one.
    assert matcher is matchers[2]
    # And it matched the first three segments
    assert len(match) == 3


def test__parser__grammar__base__ephemeral_segment(seg_list):
    """Test the ephemeral features on BaseGrammar.

    Normally you can't call .match() on a BaseGrammar, but
    if things are set up right, then it should be possible
    in the case that the ephemeral_name is set.

    This indirectly tests the allow_ephemeral decorator.
    """
    g = BaseGrammar(ephemeral_name="TestGrammar")

    ctx = ParseContext(dialect=None)
    m = g.match(seg_list, ctx)
    # Check we get an ephemeral segment
    assert isinstance(m.matched_segments[0], EphemeralSegment)
    assert len(m.matched_segments) == 1
    chkpoint = m.matched_segments[0]
    # Check it's got the same content.
    assert chkpoint.segments == seg_list
