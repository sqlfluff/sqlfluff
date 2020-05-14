"""Tests for bigquery dialect."""

import pytest

from .dialects_ansi_test import check_parse_match


# Develop test to check specific elements against specific grammars.
@pytest.mark.parametrize(
    "segmentref,raw",
    [
        # Composite data types
        ("DatatypeSegment", "INT64"),
        ("DatatypeSegment", "ARRAY<INT64>"),
        ("DatatypeSegment", "STRUCT<product_id INT64, user_id INT64>"),
        ("DatatypeSegment", "ARRAY<STRUCT<product_id INT64, rating FLOAT64>>"),
    ]
)
def test__dialect__bigquery_specific_segment_parses(segmentref, raw, caplog):
    """Test that specific segments parse as expected.

    NB: We're testing the PARSE function not the MATCH function
    although this will be a recursive parse and so the match
    function of SUBSECTIONS will be tested if present. The match
    function of the parent will not be tested.
    """
    parsed = check_parse_match(raw, segmentref, caplog, dialect='bigquery')
    # Check that there's nothing un parsable
    typs = parsed.type_set()
    assert 'unparsable' not in typs
