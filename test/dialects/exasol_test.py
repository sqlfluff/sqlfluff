"""Tests specific to the exasol dialect."""

import pytest

TEST_DIALECT = "exasol"


# Develop test to check specific elements against specific grammars.
@pytest.mark.parametrize(
    "segmentref,raw",
    [
        ("RangeOperator", ".."),
        ("WalrusOperatorSegment", ":="),
        ("VariableNameSegment", "var1"),
    ],
)
def test_dialect_exasol_specific_segment_parses(
    segmentref, raw, caplog, dialect_specific_segment_parses
):
    """Test exasol specific segments."""
    dialect_specific_segment_parses(TEST_DIALECT, segmentref, raw, caplog)
