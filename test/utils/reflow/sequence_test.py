"""Tests for the reflow module."""

import logging

import pytest

from sqlfluff.core import Linter
from sqlfluff.core.rules.base import LintFix
from sqlfluff.utils.reflow.elements import ReflowBlock, ReflowPoint
from sqlfluff.utils.reflow.sequence import ReflowSequence


def parse_ansi_string(sql, config):
    """Parse an ansi sql string for testing."""
    linter = Linter(config=config)
    return linter.parse_string(sql).tree


def assert_reflow_structure(sequence, StartClass, raw_elems):
    """Assert a ReflowSequence has the defined structure."""
    assert [
        [seg.raw for seg in elem.segments] for elem in sequence.elements
    ] == raw_elems
    # We can assert all the classes just by knowing which we should start with
    assert all(type(elem) is StartClass for elem in sequence.elements[::2])
    OtherClass = ReflowBlock if StartClass is ReflowPoint else ReflowPoint
    assert all(type(elem) is OtherClass for elem in sequence.elements[1::2])


@pytest.mark.parametrize(
    "raw_sql,StartClass,raw_elems",
    [
        (
            "select 1 +2",
            ReflowBlock,
            [
                ["select"],
                # NOTE: The empty strings are indents and dedents
                ["", " "],
                ["1"],
                [" "],
                ["+"],
                [],
                ["2"],
                # indent (as point)
                [""],
                # end_of_file (as block)
                [""],
            ],
        )
    ],
)
def test_reflow_sequence_from_segments(
    raw_sql, StartClass, raw_elems, default_config, caplog
):
    """Test direct sequence construction from segments."""
    root = parse_ansi_string(raw_sql, default_config)
    with caplog.at_level(logging.DEBUG, logger="sqlfluff.rules.reflow"):
        result = ReflowSequence.from_raw_segments(
            root.raw_segments, root, config=default_config
        )
    assert_reflow_structure(result, StartClass, raw_elems)


@pytest.mark.parametrize(
    "raw_sql,sides,target_idx,target_raw,StartClass,raw_elems",
    [
        (
            "select 1 +2",
            "both",
            5,
            "+",
            ReflowBlock,
            [
                # We should have expanded as far as the blocks either side
                ["1"],
                [" "],
                ["+"],
                [],
                ["2"],
            ],
        ),
        (
            "select 1 +2",
            "before",
            5,
            "+",
            ReflowBlock,
            [
                ["1"],
                [" "],
                ["+"],
            ],
        ),
        (
            "select 1 +2",
            "after",
            5,
            "+",
            ReflowBlock,
            [
                ["+"],
                [],
                ["2"],
            ],
        ),
        (
            "select 1 +2",
            "before",
            6,
            "2",
            ReflowBlock,
            [
                ["+"],
                [],
                ["2"],
            ],
        ),
        (
            "select 1 +2",
            "both",
            4,
            " ",
            ReflowBlock,
            [
                # Even targeting whitespace, we should get points either side.
                ["1"],
                [" "],
                ["+"],
            ],
        ),
        (
            "select (1+2)",
            "both",
            5,
            "1",
            ReflowBlock,
            [
                # NOTE: We don't just stop at the indent, we go as far as code.
                ["("],
                # The indent sits in the point.
                [""],
                ["1"],
                [],
                ["+"],
            ],
        ),
        (
            "     SELECT 1     ",
            "both",
            1,
            "SELECT",
            ReflowPoint,
            [
                # We'll hit the edge of the file so start with a point.
                ["     "],
                ["SELECT"],
                ["", " "],
                ["1"],
            ],
        ),
    ],
)
def test_reflow_sequence_from_around_target(
    raw_sql,
    sides,
    target_idx,
    target_raw,
    StartClass,
    raw_elems,
    default_config,
    caplog,
):
    """Test direct sequence construction from a target."""
    root = parse_ansi_string(raw_sql, default_config)
    print("Raw Segments:", root.raw_segments)
    target = root.raw_segments[target_idx]
    # Check we're aiming at the right place
    assert target.raw == target_raw
    with caplog.at_level(logging.DEBUG, logger="sqlfluff.rules.reflow"):
        result = ReflowSequence.from_around_target(
            target, root, config=default_config, sides=sides
        )
    assert_reflow_structure(result, StartClass, raw_elems)


def test_reflow_sequence_from_around_target_non_raw(default_config, caplog):
    """Test direct sequence construction from a target.

    This time we use a target which isn't a RawSegment.
    """
    sql = "     SELECT 1     "
    root = parse_ansi_string(sql, default_config)
    # We should have a statement as a first level child.
    statement = root.segments[1]
    assert statement.is_type("statement")
    assert statement.raw == "SELECT 1"
    with caplog.at_level(logging.DEBUG, logger="sqlfluff.rules.reflow"):
        result = ReflowSequence.from_around_target(
            statement, root, config=default_config
        )
    # We should start with a point, because we hit the start of the file.
    # It should also hit the end of the file and effectively cover all
    # the raw segments of the file.
    assert_reflow_structure(
        result,
        ReflowPoint,
        [
            ["     "],
            ["SELECT"],
            ["", " "],
            ["1"],
            # dedent - ws
            ["", "     "],
            # end of file
            [""],
        ],
    )


@pytest.mark.parametrize(
    "raw_sql,filter,delete_indices,edit_indices",
    [
        # NOTE: These tests rely on the position of code *and non code* elements
        # in the parsed sequence, so may need to be altered if the parse structure
        # changes.
        ("SELECT      \n   4", "all", [2], []),
        ("SELECT \n 4, \n 6", "all", [2, 7], []),
        ("SELECT \n 4, \n 6  ", "all", [2, 7, 12], []),
        ("SELECT \n 4, 5,  6   ,    7 \n 6  ", "newline", [2, 17, 21], []),
        ("SELECT \n 4, 5,  6   ,    7 \n 6  ", "inline", [12], [10, 14]),
        ("SELECT \n 4, 5,  6    ,    7 \n 6  ", "all", [2, 12, 17, 21], [10, 14]),
    ],
)
def test_reflow_sequence_respace_filter(
    raw_sql, filter, delete_indices, edit_indices, default_config, caplog
):
    """Test iteration of trailing whitespace fixes."""
    root = parse_ansi_string(raw_sql, default_config)
    with caplog.at_level(logging.DEBUG, logger="sqlfluff.rules.reflow"):
        sequence = ReflowSequence.from_root(root, config=default_config)
    fixes = sequence.respace(filter=filter).get_fixes()

    # assert deletes
    assert [fix for fix in fixes if fix.edit_type == "delete"] == [
        LintFix("delete", root.raw_segments[idx]) for idx in delete_indices
    ]
    # assert edits (with slightly less detail)
    assert [
        root.raw_segments.index(fix.anchor)
        for fix in fixes
        if fix.edit_type == "replace"
    ] == edit_indices
