"""Tests for the SQLFluff integration with the "diff-quality" tool."""

from pathlib import Path

import pytest

from sqlfluff import diff_quality_plugin


@pytest.mark.parametrize(
    "sql_path,expected_violations_lines",
    [
        ("linter/indentation_errors.sql", list(range(2, 7))),
        ("linter/parse_error.sql", {1}),
        # NB: This version of the file is in a directory configured
        # to ignore parsing errors.
        ("linter/diffquality/parse_error.sql", []),
    ],
)
def test_diff_quality_plugin(sql_path, expected_violations_lines, monkeypatch):
    """Test the plugin at least finds errors on the expected lines."""
    monkeypatch.chdir("test/fixtures/")
    violation_reporter = diff_quality_plugin.diff_cover_report_quality(
        options="--processes=1"
    )
    sql_path = str(Path(sql_path))

    violations_dict = violation_reporter.violations_batch([sql_path])
    assert isinstance(violations_dict, dict)
    if expected_violations_lines:
        assert len(violations_dict[sql_path]) > 0
        violations_lines = {v.line for v in violations_dict[sql_path]}
        for expected_line in expected_violations_lines:
            assert expected_line in violations_lines
    else:
        assert len(violations_dict[sql_path]) == 0
