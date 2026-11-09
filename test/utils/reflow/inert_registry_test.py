"""Tests for the inert indent registry used by the reflow machinery."""

import gc

from sqlfluff.core import FluffConfig, Linter
from sqlfluff.core.parser import BaseSegment
from sqlfluff.utils.reflow.depthmap import DepthMap
from sqlfluff.utils.reflow.elements import _inert_indent_uuids, _mark_inert_indents


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
