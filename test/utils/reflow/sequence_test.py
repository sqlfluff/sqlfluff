"""Tests for the reflow module."""

import gc
import logging
import weakref
from unittest.mock import patch

import pytest

from sqlfluff.core import Linter
from sqlfluff.core.parser import WhitespaceSegment
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


class _SubclassedReflowSequence(ReflowSequence):
    """A subclass of ReflowSequence, which could build its elements differently."""


@pytest.fixture()
def empty_from_root_cache():
    """Start with nothing kept from earlier `ReflowSequence.from_root()` calls."""
    with patch("sqlfluff.utils.reflow.sequence._from_root_cache", None):
        yield


def test_reflow_sequence_from_root_shares_elements(
    default_config, empty_from_root_cache
):
    """Sequences of the same unchanged tree share elements, not lists or maps."""
    root = parse_ansi_string("select 1 +2", default_config)
    first = ReflowSequence.from_root(root, config=default_config)
    second = ReflowSequence.from_root(root, config=default_config)
    assert second.elements is not first.elements
    assert len(second.elements) == len(first.elements)
    assert all(a is b for a, b in zip(first.elements, second.elements))
    assert second.depth_map is not first.depth_map
    assert second.depth_map.depth_info == first.depth_map.depth_info


@pytest.mark.parametrize(
    "change",
    ["new_root", "root_edited", "config_edited", "layout_edited", "subclass"],
)
def test_reflow_sequence_from_root_rebuilds_after_change(
    change, default_config, empty_from_root_cache
):
    """Sequences aren't shared once the tree, the config or the class changes."""
    root = parse_ansi_string("select 1 +2", default_config)
    first = ReflowSequence.from_root(root, config=default_config)
    sequence_class = ReflowSequence
    if change == "new_root":
        # A fixed tree is always a new root object.
        root = root.copy()
    elif change == "root_edited":
        # As apply_fixes() does to the tree it is given.
        root.invalidate_caches()
    elif change == "config_edited":
        default_config.set_value(["indentation", "tab_space_size"], 2)
    elif change == "layout_edited":
        default_config.set_value(
            ["layout", "type", "comma", "spacing_before"], "single"
        )
    else:
        sequence_class = _SubclassedReflowSequence
    second = sequence_class.from_root(root, config=default_config)
    assert type(second) is sequence_class
    assert not any(a is b for a, b in zip(first.elements, second.elements))


def test_reflow_sequence_from_root_edits_stay_local(
    default_config, empty_from_root_cache
):
    """Editing one sequence's elements or depth map doesn't change another's."""
    root = parse_ansi_string("select 1 +2", default_config)
    first = ReflowSequence.from_root(root, config=default_config)
    second = ReflowSequence.from_root(root, config=default_config)
    new_segments = []
    for sequence in (first, second):
        sequence.elements.pop()
        # Edits such as insert() and replace() add depth info for new segments.
        new_segments.append(WhitespaceSegment())
        sequence.depth_map.copy_depth_info(
            root.raw_segments[0], new_segments[-1], trim=1
        )
    third = ReflowSequence.from_root(root, config=default_config)
    assert len(third.elements) == len(first.elements) + 1
    for new_segment in new_segments:
        assert new_segment.uuid not in third.depth_map.depth_info


def test_reflow_sequence_from_root_forgets_freed_tree(
    default_config, empty_from_root_cache
):
    """Nothing kept from a tree stays in memory once the tree is freed."""
    root = parse_ansi_string("select 1 +2", default_config)
    ReflowSequence.from_root(root, config=default_config)
    raw_segment = weakref.ref(root.raw_segments[0])
    del root
    gc.collect()
    assert raw_segment() is None


@pytest.mark.parametrize("marker", ["indent", "dedent"])
def test_reflow_respace_preserves_trailing_indent_marker(marker, default_config):
    """A focused sequence ending in a grammar marker must not gain a space."""
    root = parse_ansi_string("SELECT foo", default_config)
    before = root.stringify()
    end = next(
        index + 1
        for index, raw in enumerate(root.raw_segments)
        if raw.get_type() == marker
    )
    sequence = ReflowSequence.from_raw_segments(
        root.raw_segments[:end], root, config=default_config
    )
    result = sequence.respace()
    assert result.get_raw() == sequence.get_raw()
    assert not result.get_fixes()
    assert result.elements[-1].segments == sequence.elements[-1].segments
    assert root.stringify() == before
