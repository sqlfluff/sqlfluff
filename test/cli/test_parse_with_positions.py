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


def test__segment_structural_simplify_with_positions():
    """Test that structural_simplify correctly handles tuples with position info."""
    from sqlfluff.core import Linter

    # Use the linter to parse actual SQL and get real segments with positions
    linter = Linter(dialect="ansi")
    parsed = linter.parse_string("SELECT 1")

    # Get the root segment
    segment = parsed.tree

    # Test as_record with include_position=True to cover line 899 in base.py
    record_with_pos = segment.as_record(include_position=True)
    assert "start_line_no" in record_with_pos
    assert "start_line_pos" in record_with_pos
    assert record_with_pos["start_line_no"] == 1
    assert record_with_pos["start_line_pos"] == 1

    # Test as_record with include_position=False to ensure backward compatibility
    record_without_pos = segment.as_record(include_position=False)
    assert "start_line_no" not in record_without_pos
    assert "start_line_pos" not in record_without_pos


def test__meta_segment_to_tuple_with_positions():
    """Test that MetaSegment.to_tuple includes positions when requested."""
    from sqlfluff.core.parser.markers import PositionMarker
    from sqlfluff.core.parser.segments.meta import Indent
    from sqlfluff.core.templaters import TemplatedFile

    # Create a templated file for position tracking
    raw_sql = "\n    SELECT 1"  # Line 2, position 1 starts here
    templated_file = TemplatedFile.from_string(raw_sql)

    # Create an Indent meta segment with position marker at line 2
    indent = Indent(
        pos_marker=PositionMarker(
            slice(1, 5),  # The indent (4 spaces starting at position 1)
            slice(1, 5),
            templated_file,
        ),
    )

    # Verify the indent has a position marker
    assert indent.pos_marker is not None, "Indent should have a position marker"

    # Test to_tuple with include_position=True to cover line 259 in meta.py
    tuple_with_pos = indent.to_tuple(include_position=True)
    assert (
        len(tuple_with_pos) == 3
    ), f"Expected 3-element tuple, got {len(tuple_with_pos)}"
    assert tuple_with_pos[0] == "indent"
    assert isinstance(
        tuple_with_pos[2], dict
    ), f"Third element should be dict, got {type(tuple_with_pos[2])}"
    assert "start_line_no" in tuple_with_pos[2]
    assert "end_line_no" in tuple_with_pos[2]
    assert tuple_with_pos[2]["start_line_no"] == 2

    # Test to_tuple with include_position=False
    tuple_without_pos = indent.to_tuple(include_position=False)
    assert len(tuple_without_pos) == 2
    assert tuple_without_pos[0] == "indent"
