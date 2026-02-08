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


def test__structural_simplify_with_2_element_tuple():
    """Test structural_simplify with 2-element tuples (backward compatible)."""
    from sqlfluff.core.parser.segments.base import BaseSegment

    # Test with a 2-element tuple (no position) - covers line 603
    elem_2 = ("keyword", "SELECT")
    result = BaseSegment.structural_simplify(elem_2)
    assert "keyword" in result
    assert result["keyword"] == "SELECT"
    # Should not have position fields
    assert "start_line_no" not in result

    # Test with nested 2-element tuples - covers line 614
    # When there are duplicate keys (two "keyword" elements), it returns a list
    nested_elem = ("statement", (("keyword", "SELECT"), ("keyword", "FROM")))
    result_nested = BaseSegment.structural_simplify(nested_elem)
    assert "statement" in result_nested
    # With duplicate subkeys, should be a list
    assert isinstance(result_nested["statement"], list)
    assert len(result_nested["statement"]) == 2


def test__structural_simplify_with_3_element_tuple():
    """Test structural_simplify with 3-element tuples (with position)."""
    from sqlfluff.core.parser.segments.base import BaseSegment

    # Test with a 3-element tuple (with position)
    position_dict = {
        "start_line_no": 1,
        "start_line_pos": 1,
        "start_file_pos": 0,
        "end_line_no": 1,
        "end_line_pos": 7,
        "end_file_pos": 6,
    }
    elem_3 = ("keyword", "SELECT", position_dict)
    result = BaseSegment.structural_simplify(elem_3)

    # Should have the keyword
    assert "keyword" in result
    assert result["keyword"] == "SELECT"

    # Should also have position fields merged in
    assert result["start_line_no"] == 1
    assert result["start_line_pos"] == 1
    assert result["end_line_no"] == 1


def test__cli_parse_includes_meta_segment_positions():
    """Test that meta segments in parsed output include pos. with --include-meta."""
    from sqlfluff.core import Linter

    # Parse SQL that will generate meta segments (indents)
    sql_with_indents = """SELECT
    col1,
    col2
FROM table1"""

    linter = Linter(dialect="ansi")
    parsed = linter.parse_string(sql_with_indents)

    # Get as_record with include_position=True and include_meta=True
    record = parsed.tree.as_record(
        code_only=False,
        show_raw=True,
        include_meta=True,
        include_position=True,
    )

    # The record should exist and have position info
    assert record is not None
    assert "start_line_no" in record

    # Look for meta segments with positions by converting to tuple first
    tuple_repr = parsed.tree.to_tuple(
        code_only=False,
        show_raw=True,
        include_meta=True,
        include_position=True,
    )

    # Recursively search for 3-element tuples (which include positions)
    def find_3_element_tuples(obj, depth=0):
        if depth > 20:  # Prevent infinite recursion
            return []
        if isinstance(obj, tuple):
            if len(obj) == 3 and isinstance(obj[2], dict):
                return [obj]
            elif len(obj) >= 2:
                results = []
                if isinstance(obj[1], tuple):
                    for item in obj[1]:
                        results.extend(find_3_element_tuples(item, depth + 1))
                return results
        return []

    tuples_with_pos = find_3_element_tuples(tuple_repr)
    # Should find at least some tuples with position information
    assert len(tuples_with_pos) > 0, "Should find segments with position information"
