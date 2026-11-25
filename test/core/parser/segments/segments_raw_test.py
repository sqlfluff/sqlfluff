"""Test the RawSegment class."""

from sqlfluff.core.parser.segments.base import PathStep
from sqlfluff.core.parser.segments.raw import RawSegment


def test__parser__raw_get_raw_segments(raw_segments):
    """Test niche case of calling get_raw_segments on a raw segment."""
    for s in raw_segments:
        assert s.get_raw_segments() == [s]


def test__parser__raw_segments_with_ancestors(
    raw_segments, DummySegment, DummyAuxSegment
):
    """Test raw_segments_with_ancestors.

    This is used in the reflow module to assess parse depth.
    """
    test_seg = DummySegment([DummyAuxSegment(raw_segments[:1]), raw_segments[1]])
    # Result should be the same raw segment, but with appropriate parents
    assert test_seg.raw_segments_with_ancestors == [
        (
            raw_segments[0],
            [
                PathStep(test_seg, 0, 2, (0, 1)),
                PathStep(test_seg.segments[0], 0, 1, (0,)),
            ],
        ),
        (raw_segments[1], [PathStep(test_seg, 1, 2, (0, 1))]),
    ]


def test__parser__raw_class_types_merge_cache():
    """RawSegment.class_types returns _class_types directly or caches merged types."""
    plain = RawSegment(raw="a")
    assert plain.class_types is plain._class_types

    seg_a = RawSegment(raw="a", instance_types=("custom_a", "custom_b"))
    seg_b = RawSegment(raw="b", instance_types=("custom_a", "custom_b"))
    expected = frozenset(("custom_a", "custom_b")) | seg_a._class_types
    assert seg_a.class_types == expected
    assert seg_a.class_types is seg_b.class_types
