"""Test sqlfluff.core.rules.base module."""
import sqlfluff.core.rules.base as rules_base


def test_whitespace_segment_is_whitespace():
    """Tests that WhitespaceSegment.is_whitespace is True."""
    assert rules_base.BaseRule.make_whitespace("", "").is_whitespace
