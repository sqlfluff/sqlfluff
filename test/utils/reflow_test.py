"""Tests for the reflow module."""

import logging
import pytest

from sqlfluff.core import Linter, FluffConfig
from sqlfluff.core.rules.base import LintFix

from sqlfluff.utils.reflow.classes import ReflowSequence, ReflowBlock, ReflowPoint


def parse_ansi_string(sql):
    """Parse an ansi sql string for testing."""
    cfg = FluffConfig(overrides={"dialect": "ansi"})
    linter = Linter(config=cfg)
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
                # NOTE: The last element is the end of file marker.
                # indent, end_of_file.
                ["", ""],
            ],
        )
    ],
)
def test_reflow_sequence_from_segments(raw_sql, StartClass, raw_elems, caplog):
    """Test direct sequence contruction from segments."""
    root = parse_ansi_string(raw_sql)
    with caplog.at_level(logging.DEBUG, logger="sqlfluff.utils.reflow"):
        result = ReflowSequence.from_raw_segments(root.raw_segments, root)
    assert_reflow_structure(result, StartClass, raw_elems)


@pytest.mark.parametrize(
    "raw_sql,target_idx,target_raw,StartClass,raw_elems",
    [
        (
            "select 1 +2",
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
            "select (1+2)",
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
    ],
)
def test_reflow_sequence_from_around_target(
    raw_sql, target_idx, target_raw, StartClass, raw_elems, caplog
):
    """Test direct sequence contruction from a target."""
    root = parse_ansi_string(raw_sql)
    target = root.raw_segments[target_idx]
    # Check we're aiming at the right place
    assert target.raw == target_raw
    with caplog.at_level(logging.DEBUG, logger="sqlfluff.utils.reflow"):
        result = ReflowSequence.from_around_target(target, root)
    assert_reflow_structure(result, StartClass, raw_elems)


@pytest.mark.parametrize(
    "raw_sql,delete_indices",
    [
        ("SELECT      \n   4", [2]),
        ("SELECT \n 4, \n 6", [2, 7]),
        ("SELECT \n 4, \n 6  ", [2, 7, 12]),
    ],
)
def test_reflow_sequence_trailing_whitespace_fixes(raw_sql, delete_indices, caplog):
    """Test direct sequence contruction from a target."""
    root = parse_ansi_string(raw_sql)
    with caplog.at_level(logging.DEBUG, logger="sqlfluff.utils.reflow"):
        sequence = ReflowSequence.from_root(root)
    fixes = sequence.trailing_whitespace_fixes()
    assert fixes == [
        LintFix("delete", root.raw_segments[idx]) for idx in delete_indices
    ]
