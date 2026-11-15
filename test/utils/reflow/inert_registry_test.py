"""Tests for the inert indent registry used by the reflow machinery."""

import gc
from typing import cast

from sqlfluff.core import FluffConfig, Linter
from sqlfluff.core.parser import BaseSegment, Indent
from sqlfluff.utils.reflow.depthmap import DepthMap
from sqlfluff.utils.reflow.elements import (
    ReflowPoint,
    _inert_indent_uuids,
    _mark_inert_indents,
)
from sqlfluff.utils.reflow.sequence import ReflowSequence


def _marked_indents(root: BaseSegment) -> list:
    """Mark the inert indents of a tree and return the marked instances."""
    segments = list(root.raw_segments)
    depth_map = DepthMap.from_parent(root)
    _mark_inert_indents(segments, depth_map)
    return [seg for seg in segments if _inert_indent_uuids.is_marked(seg.uuid)]


def test_inert_indent_marking_survives_tree_copies():
    """A copy of a parse tree shares the uuid of its source.

    `BaseSegment.copy()` preserves uuids, so after re-marking a deep
    copy of a tree, the still-live original must keep its inert marking
    once the copy is freed. This is what made a plain
    WeakValueDictionary unsafe for this registry: the copy overwrote
    the weak value for the original, and freeing the copy dropped the
    entry entirely.
    """
    config = FluffConfig(overrides={"dialect": "snowflake"})
    linter = Linter(config=config)
    root = linter.parse_string("SELECT * FROM (VALUES ('v1')) AS x;").tree

    original_marked = _marked_indents(root)
    assert original_marked, "expected the bracketed VALUES indents to be marked"

    # A deep copy consists of new instances carrying the same uuids.
    copied_tree = root.copy()
    copied_marked = _marked_indents(copied_tree)
    assert [seg.uuid for seg in copied_marked] == [seg.uuid for seg in original_marked]
    assert copied_marked[0] is not original_marked[0]

    # Free the copies (their parent links form cycles, hence gc); the
    # original tree must keep its marking.
    del copied_tree, copied_marked
    gc.collect()

    for seg in original_marked:
        assert _inert_indent_uuids.is_marked(seg.uuid), (
            f"uuid {seg.uuid} lost its marking once its copy was freed"
        )


def test_inert_indent_registry_prunes_dead_buckets_eagerly():
    """Dead uuid buckets are pruned by the weakref removal callbacks.

    The registry is global and lives for the whole process, so without
    a removal callback a bucket whose last live instance had been
    freed would linger until that uuid happened to be looked up again
    -- and would linger forever for uuids which never are.
    """
    config = FluffConfig(overrides={"dialect": "snowflake"})
    linter = Linter(config=config)
    root = linter.parse_string("SELECT * FROM (VALUES ('v1')) AS x;").tree
    marked = _marked_indents(root)
    assert marked, "expected the bracketed VALUES indents to be marked"

    # Free the whole tree (parent links form cycles, hence gc). The
    # weakref callbacks must then prune every bucket eagerly, even
    # though none of these uuids is looked up afterwards.
    uuids = [seg.uuid for seg in marked]
    del root, marked
    gc.collect()

    for uuid in uuids:
        assert uuid not in _inert_indent_uuids._refs, (
            f"bucket for uuid {uuid} was not pruned once its tree was freed"
        )


def test_get_indent_segment_vals_skips_marked_indents():
    """`ReflowPoint.get_indent_segment_vals` skips marked inert indents.

    The wiggle-room paths in `reindent.py` sum indent values point by
    point, so a marked (inert) indent must contribute nothing there
    either -- exactly as in `_generate_indent_stats`.
    """
    config = FluffConfig(overrides={"dialect": "snowflake"})
    linter = Linter(config=config)
    root = linter.parse_string(
        "SELECT *\nFROM (\n    VALUES\n        ('v1', 'v2')\n) AS x (c1, c2);"
    ).tree
    seq = ReflowSequence.from_root(root, config=config)

    marked = {
        seg.uuid
        for seg in root.raw_segments
        if seg.is_type("indent") and _inert_indent_uuids.is_marked(seg.uuid)
    }
    assert marked, "expected the bracketed VALUES indents to be marked"

    points_with_marked = 0
    for elem in seq.elements:
        if not isinstance(elem, ReflowPoint):
            continue
        indent_segs = [cast(Indent, s) for s in elem.segments if s.is_type("indent")]
        marked_here = {s.uuid for s in indent_segs} & marked
        if not marked_here:
            continue
        points_with_marked += 1
        # Marked indents contribute nothing; every unmarked indent in
        # the same point (e.g. the enclosing bracket's own Dedent) still
        # contributes its value, with and without block indents.
        expected = [s.indent_val for s in indent_segs if s.uuid not in marked_here]
        assert elem.get_indent_segment_vals() == expected
        expected_no_block = [
            s.indent_val
            for s in indent_segs
            if s.uuid not in marked_here and not s.block_uuid
        ]
        assert (
            elem.get_indent_segment_vals(exclude_block_indents=True)
            == expected_no_block
        )
    assert points_with_marked, "no reflow point carried a marked indent"
