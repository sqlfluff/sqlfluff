"""Tests for the reflow module."""

import gc
import logging
import weakref
from unittest.mock import patch

import pytest

from sqlfluff.core import FluffConfig, Linter
from sqlfluff.core.parser import Indent, WhitespaceSegment
from sqlfluff.core.rules.base import LintFix
from sqlfluff.utils.reflow.config import (
    _DEFAULT_BLOCK_CONFIG,
    _EMPTY_LIST_BLOCK_CONFIG,
    BlockConfig,
)
from sqlfluff.utils.reflow.elements import (
    _EMPTY_INDENT_STATS,
    IndentStats,
    ReflowBlock,
    ReflowPoint,
)
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


def test_reflow_elements_parent_config_cache_matches_uncached(default_config):
    """Cached parent stack configs match uncached ReflowBlock.from_config()."""
    sql = (
        "WITH cte AS (\n"
        "    SELECT a + b AS x, COALESCE(c, d) AS y\n"
        "    FROM tbl\n"
        "    WHERE e = 1 AND f IN (1, 2, 3)\n"
        ")\n"
        "SELECT * FROM cte ORDER BY x DESC\n"
    )
    root = parse_ansi_string(sql, default_config)
    seq = ReflowSequence.from_root(root, config=default_config)
    blocks_by_raw: dict[str, ReflowBlock] = {}
    for elem in seq.elements:
        if isinstance(elem, ReflowBlock):
            uncached = ReflowBlock.from_config(
                segments=elem.segments,
                config=seq.reflow_config,
                depth_info=elem.depth_info,
            )
            assert elem == uncached
            blocks_by_raw.setdefault(elem.raw, elem)

    # Literal expected values under default config (including exclusions parity
    # and parent-inherited spacing on function brackets).
    assert blocks_by_raw["SELECT"].spacing_before == "single"
    assert blocks_by_raw["SELECT"].spacing_after == "single"
    assert blocks_by_raw["SELECT"].keyword_line_position_exclusions == []
    assert blocks_by_raw[","].spacing_before == "touch"
    assert blocks_by_raw[","].spacing_after == "single"
    assert blocks_by_raw[","].line_position == "trailing"
    assert blocks_by_raw[","].keyword_line_position_exclusions == []
    assert blocks_by_raw["+"].line_position == "leading"
    assert blocks_by_raw["a"].keyword_line_position_exclusions == []
    lparen_blocks = [
        elem
        for elem in seq.elements
        if isinstance(elem, ReflowBlock) and elem.raw == "("
    ]
    assert lparen_blocks[0].spacing_before == "single"
    assert lparen_blocks[0].spacing_after == "touch"
    assert lparen_blocks[1].spacing_before == "touch:inline"
    assert lparen_blocks[1].spacing_after == "touch"
    assert lparen_blocks[1].keyword_line_position_exclusions == []

    # Non-default layout config exercising keyword_line_position and exclusions.
    custom_cfg = FluffConfig(
        overrides={"dialect": "ansi"},
        configs={
            "layout": {
                "type": {
                    "from_clause": {
                        "keyword_line_position": "alone",
                        "keyword_line_position_exclusions": "where_clause,join_clause",
                    },
                    "where_clause": {"keyword_line_position": "leading"},
                }
            }
        },
    )
    custom_root = parse_ansi_string("SELECT a FROM t WHERE b = 1\n", custom_cfg)
    custom_seq = ReflowSequence.from_root(custom_root, config=custom_cfg)
    custom_blocks = {
        elem.raw: elem for elem in custom_seq.elements if isinstance(elem, ReflowBlock)
    }
    assert list(custom_blocks["FROM"].keyword_line_position_configs.values()) == [
        "alone"
    ]
    assert list(
        custom_blocks["FROM"].keyword_line_position_exclusions_configs.values()
    ) == [["where_clause", "join_clause"]]
    assert list(custom_blocks["WHERE"].keyword_line_position_configs.values()) == [
        "leading"
    ]
    for elem in custom_blocks.values():
        assert elem == ReflowBlock.from_config(
            segments=elem.segments,
            config=custom_seq.reflow_config,
            depth_info=elem.depth_info,
        )

    # Public get_block_config() and ReflowBlock.from_config() must return fresh
    # configs that callers can mutate without affecting shared read-only defaults.
    fresh_default = seq.reflow_config.get_block_config(set())
    assert fresh_default is not _DEFAULT_BLOCK_CONFIG
    fresh_default.incorporate(before="touch")
    assert _DEFAULT_BLOCK_CONFIG == BlockConfig()
    assert seq.reflow_config.get_block_config(set()) == BlockConfig()

    fresh_parent_default = seq.reflow_config.get_block_config(
        set(), depth_info=blocks_by_raw["a"].depth_info
    )
    assert fresh_parent_default is not _EMPTY_LIST_BLOCK_CONFIG
    assert isinstance(fresh_parent_default.keyword_line_position_exclusions, list)
    assert (
        fresh_parent_default.keyword_line_position_exclusions
        is not _EMPTY_LIST_BLOCK_CONFIG.keyword_line_position_exclusions
    )
    fresh_parent_default.keyword_line_position_exclusions.append("mutated")
    assert _EMPTY_LIST_BLOCK_CONFIG == BlockConfig(keyword_line_position_exclusions=[])

    fresh_block = ReflowBlock.from_config(
        segments=blocks_by_raw["a"].segments,
        config=seq.reflow_config,
        depth_info=blocks_by_raw["a"].depth_info,
    )
    assert (
        fresh_block.keyword_line_position_exclusions
        is not _EMPTY_LIST_BLOCK_CONFIG.keyword_line_position_exclusions
    )


def test_reflow_point_lazy_indent_stats():
    """ReflowPoint computes _stats lazily without affecting repr, ==, or hash."""
    ws_segs = (WhitespaceSegment(" "),)
    pt_a = ReflowPoint(ws_segs)
    pt_b = ReflowPoint(ws_segs)
    assert pt_a._stats is None
    assert "_stats" not in repr(pt_a)

    stats = pt_a.get_indent_impulse()
    assert stats is _EMPTY_INDENT_STATS
    assert pt_a._stats is _EMPTY_INDENT_STATS
    assert pt_b._stats is None
    assert pt_a == pt_b
    assert hash(pt_a) == hash(pt_b)

    indent_segs = (Indent(), WhitespaceSegment("    "))
    indent_a = ReflowPoint(indent_segs)
    indent_b = ReflowPoint(indent_segs)
    assert indent_a._stats is None
    assert indent_a.get_indent_impulse() == IndentStats(1, 0)
    assert indent_b._stats is None
    assert indent_a == indent_b
    assert hash(indent_a) == hash(indent_b)
