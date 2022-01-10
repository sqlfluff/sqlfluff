"""Tests specific to the oracle dialect."""

import pytest


# Develop test to check specific elements against specific grammars.
@pytest.mark.parametrize(
    "segmentref,raw",
    [
        ("PromptStatementSegment", "PROMPT this is an arbitrary string"),
        ("CommentStatementSegment", "COMMENT ON TABLE foo IS 'this is an arbitrary string'"),
    ],
)

def test__dialect__oracle_specific_segment_parses(
    segmentref, raw, caplog, dialect_specific_segment_parses
):
    """Test that specific segments parse as expected.

    NB: We're testing the PARSE function not the MATCH function
    although this will be a recursive parse and so the match
    function of SUBSECTIONS will be tested if present. The match
    function of the parent will not be tested.
    """
    dialect_specific_segment_parses("oracle", segmentref, raw, caplog)
