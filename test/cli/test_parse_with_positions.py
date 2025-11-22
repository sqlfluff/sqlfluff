"""Test that parse command includes position information with --include-meta flag."""

import json

import pytest
import yaml

from sqlfluff.cli.commands import parse
from test.cli.commands_test import invoke_assert_code


@pytest.mark.parametrize("serialize", ["json", "yaml"])
def test__cli__command_parse_with_include_meta_has_positions(serialize):
    """Test that --include-meta includes position info in output."""
    cmd_args = ("-", "--format", serialize, "--include-meta", "--dialect=ansi")

    result = invoke_assert_code(
        args=[parse, cmd_args],
        cli_input="SELECT * FROM tbl",
    )

    if serialize == "json":
        parsed_result = json.loads(result.stdout)
    elif serialize == "yaml":
        parsed_result = yaml.safe_load(result.stdout)
    else:
        raise Exception(f"Unexpected serialize format: {serialize}")

    # Get the segments from the first file
    result_data = parsed_result[0]
    assert result_data["filepath"] == "stdin"
    segments = result_data["segments"]

    # Check that top-level segment has position information
    assert "start_line_no" in segments
    assert "start_line_pos" in segments
    assert "start_file_pos" in segments
    assert "end_line_no" in segments
    assert "end_line_pos" in segments
    assert "end_file_pos" in segments

    # Verify the position values are reasonable for our test SQL
    assert segments["start_line_no"] == 1
    assert segments["start_line_pos"] == 1
    assert segments["start_file_pos"] == 0
    assert segments["end_line_no"] >= 1
    assert segments["end_file_pos"] > 0


@pytest.mark.parametrize("serialize", ["json", "yaml"])
def test__cli__command_parse_without_include_meta_no_positions(serialize):
    """Test that WITHOUT --include-meta flag, position information is NOT included."""
    cmd_args = ("-", "--format", serialize, "--dialect=ansi")

    result = invoke_assert_code(
        args=[parse, cmd_args],
        cli_input="SELECT * FROM tbl",
    )

    if serialize == "json":
        parsed_result = json.loads(result.stdout)
    elif serialize == "yaml":
        parsed_result = yaml.safe_load(result.stdout)
    else:
        raise Exception(f"Unexpected serialize format: {serialize}")

    # Get the segments from the first file
    result_data = parsed_result[0]
    assert result_data["filepath"] == "stdin"
    segments = result_data["segments"]

    # Check that top-level segment does NOT have position information
    assert "start_line_no" not in segments
    assert "start_line_pos" not in segments
    assert "start_file_pos" not in segments
    assert "end_line_no" not in segments
    assert "end_line_pos" not in segments
    assert "end_file_pos" not in segments


def test__cli__command_parse_position_accuracy():
    """Test that position information is accurate for specific segments."""
    # Use a multi-line SQL to test line number tracking
    sql_input = """SELECT col1,
       col2
FROM my_table"""

    cmd_args = ("-", "--format", "json", "--include-meta", "--dialect=ansi")

    result = invoke_assert_code(
        args=[parse, cmd_args],
        cli_input=sql_input,
    )

    parsed_result = json.loads(result.stdout)
    segments = parsed_result[0]["segments"]

    # The file segment should span all lines
    assert segments["start_line_no"] == 1
    assert segments["end_line_no"] == 3  # Last line of input

    # Verify the file segment position values make sense
    assert segments["start_line_pos"] == 1
    assert segments["start_file_pos"] == 0
    # end_file_pos should be at or near the end of the input
    assert segments["end_file_pos"] >= len(sql_input.rstrip())
