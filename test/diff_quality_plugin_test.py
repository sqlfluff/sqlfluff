"""Tests for the SQLFluff integration with the "diff-quality" tool."""

import sys

import pytest

try:
    from sqlfluff import diff_quality_plugin
except ImportError:
    pass


@pytest.mark.parametrize(
    "sql_path,expected_violations_lines",
    [
        ("test/fixtures/linter/indentation_errors.sql", list(range(2, 7))),
        ("test/fixtures/linter/parse_error.sql", {1}),
        # NB: This version of the file is in a directory configured
        # to ignore parsing errors.
        ("test/fixtures/linter/diffquality/parse_error.sql", []),
    ],
)
@pytest.mark.skipif(
    sys.version_info[:2] == (3, 4),
    reason="requires diff_cover package, which does not support python3.4",
)
def test_diff_quality_plugin(sql_path, expected_violations_lines):
    """Test the plugin at least finds errors on the expected lines."""
    violation_reporter = diff_quality_plugin.diff_cover_report_quality()
    violations = violation_reporter.violations(sql_path)
    assert isinstance(violations, list)
    if expected_violations_lines:
        assert len(violations) > 0
        violations_lines = {v.line for v in violations}
        for expected_line in expected_violations_lines:
            assert expected_line in violations_lines
    else:
        assert len(violations) == 0
