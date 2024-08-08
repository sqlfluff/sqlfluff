"""Tests for the SQLFluff integration with the "diff-quality" tool."""

import sys
from pathlib import Path

import pytest

from sqlfluff import diff_quality_plugin
from sqlfluff.cli.commands import lint
from sqlfluff.utils.testing.cli import invoke_assert_code


@pytest.mark.parametrize(
    "sql_paths,expected_violations_lines",
    [
        (("linter/indentation_errors.sql",), list(range(2, 7))),
        (("linter/parse_error.sql",), {1}),
        # NB: This version of the file is in a directory configured
        # to ignore parsing errors.
        (("linter/diffquality/parse_error.sql",), []),
        (tuple(), []),
    ],
)
def test_diff_quality_plugin(sql_paths, expected_violations_lines, monkeypatch):
    """Test the plugin at least finds errors on the expected lines."""

    def execute(command, exit_codes):
        printable_command_parts = [
            c.decode(sys.getfilesystemencoding()) if isinstance(c, bytes) else c
            for c in command
        ]

        result = invoke_assert_code(
            ret_code=1 if expected_violations_lines else 0,
            args=[
                lint,
                printable_command_parts[2:],
            ],
        )
        return result.output, ""

    # Mock the execute function -- this is an attempt to prevent the CircleCI
    # coverage check from hanging. (We've seen issues in the past where using
    # subprocesses caused things to occasionally hang.)
    monkeypatch.setattr(diff_quality_plugin, "execute", execute)
    monkeypatch.chdir("test/fixtures/")
    violation_reporter = diff_quality_plugin.diff_cover_report_quality(
        options="--processes=1"
    )
    assert len(sql_paths) in (0, 1)
    sql_paths = [str(Path(sql_path)) for sql_path in sql_paths]

    violations_dict = violation_reporter.violations_batch(sql_paths)
    assert isinstance(violations_dict, dict)
    if expected_violations_lines:
        assert len(violations_dict[sql_paths[0]]) > 0
        violations_lines = {v.line for v in violations_dict[sql_paths[0]]}
        for expected_line in expected_violations_lines:
            assert expected_line in violations_lines
    else:
        assert (
            len(violations_dict[sql_paths[0]]) == 0
            if sql_paths
            else len(violations_dict) == 0
        )
