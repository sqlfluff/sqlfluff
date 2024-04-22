"""Tests for the depthmap object."""

from sqlfluff.core import Linter
from sqlfluff.utils.reflow.depthmap import DepthMap, StackPosition


def parse_ansi_string(sql, config):
    """Parse an ansi sql string for testing."""
    linter = Linter(config=config)
    return linter.parse_string(sql).root_variant().tree


def test_reflow_depthmap_from_parent(default_config):
    """Test map construction from a root segment."""
    sql = "SELECT 1"
    root = parse_ansi_string(sql, default_config)

    dm = DepthMap.from_parent(root)

    # We use UUIDS in the depth map so we can't assert their value.
    # What we can do is use them.

    # Check that we get the right depths.
    assert [dm.depth_info[seg.uuid].stack_depth for seg in root.raw_segments] == [
        4,
        4,
        4,
        5,
        4,
        1,
    ]
    # Check they all share the same first three hash and
    # class type elements (except the end of file marker at the end).
    # These should be the file, statement and select statement.
    expected = ({"file", "base"}, {"statement", "base"}, {"select_statement", "base"})
    assert all(
        dm.depth_info[seg.uuid].stack_class_types[:3] == expected
        for seg in root.raw_segments[:-1]
    )
    first_hashes = dm.depth_info[root.raw_segments[0].uuid].stack_hashes[:3]
    assert all(
        dm.depth_info[seg.uuid].stack_hashes[:3] == first_hashes
        for seg in root.raw_segments[:-1]
    )

    # While we're here, test the DepthInfo.common_with method
    select_keyword_di = dm.depth_info[root.raw_segments[0].uuid]
    numeric_one_di = dm.depth_info[root.raw_segments[3].uuid]
    assert len(select_keyword_di.common_with(numeric_one_di)) == 4


def test_reflow_depthmap_from_raws_and_root(default_config):
    """Test that the indirect route is equivalent to the direct route."""
    sql = "SELECT 1"
    root = parse_ansi_string(sql, default_config)

    # Direct route
    dm_direct = DepthMap.from_parent(root)

    # Indirect route.
    dm_indirect = DepthMap.from_raws_and_root(root.raw_segments, root)

    # The depth info dict depends on the sequence so we only need
    # to check those are equal.
    assert dm_direct.depth_info == dm_indirect.depth_info


def test_reflow_depthmap_order_by(default_config):
    """Test depth mapping of an order by clause."""
    sql = "SELECT * FROM foo ORDER BY bar DESC\n"
    root = parse_ansi_string(sql, default_config)
    # Get the `ORDER` and `DESC` segments.
    order_seg = None
    desc_seg = None
    for raw in root.raw_segments:
        if raw.raw_upper == "ORDER":
            order_seg = raw
        elif raw.raw_upper == "DESC":
            desc_seg = raw
    # Make sure we find them
    assert order_seg
    assert desc_seg

    # Generate a depth map
    depth_map = DepthMap.from_parent(root)
    # Check their depth info
    order_seg_di = depth_map.get_depth_info(order_seg)
    desc_seg_di = depth_map.get_depth_info(desc_seg)
    # Make sure they both contain an order by clause.
    assert frozenset({"base", "orderby_clause"}) in order_seg_di.stack_class_types
    assert frozenset({"base", "orderby_clause"}) in desc_seg_di.stack_class_types
    # Get the ID of one and make sure it's in the other
    order_by_hash = order_seg_di.stack_hashes[
        order_seg_di.stack_class_types.index(frozenset({"base", "orderby_clause"}))
    ]
    assert order_by_hash in order_seg_di.stack_hashes
    assert order_by_hash in desc_seg_di.stack_hashes
    # Get the position information
    order_stack_pos = order_seg_di.stack_positions[order_by_hash]
    desc_stack_pos = desc_seg_di.stack_positions[order_by_hash]
    # Make sure the position information is correct
    print(order_stack_pos)
    print(desc_stack_pos)
    assert order_stack_pos == StackPosition(idx=0, len=9, type="start")
    # NOTE: Even though idx 7 is not the end, the _type_ of this location
    # is still an "end" because the following elements are non-code.
    assert desc_stack_pos == StackPosition(idx=7, len=9, type="end")
