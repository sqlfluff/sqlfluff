"""Tests for meta segment position handling."""

from sqlfluff.core.parser.markers import PositionMarker
from sqlfluff.core.parser.segments.meta import Dedent, EndOfFile, Indent
from sqlfluff.core.templaters import TemplatedFile


def test_meta_segment_to_tuple_with_position():
    """Test that MetaSegment.to_tuple includes position when requested."""
    raw_sql = "SELECT 1"
    templated_file = TemplatedFile.from_string(raw_sql)

    # Create meta segments with position markers
    indent = Indent(
        pos_marker=PositionMarker(
            slice(0, 0),
            slice(0, 0),
            templated_file,
        ),
    )

    dedent = Dedent(
        pos_marker=PositionMarker(
            slice(8, 8),
            slice(8, 8),
            templated_file,
        ),
    )

    eof = EndOfFile(
        pos_marker=PositionMarker(
            slice(8, 8),
            slice(8, 8),
            templated_file,
        ),
    )

    # Test with include_meta=True
    for meta_seg, expected_type in [
        (indent, "indent"),
        (dedent, "dedent"),
        (eof, "end_of_file"),
    ]:
        tuple_with_pos = meta_seg.to_tuple(include_meta=True)
        assert len(tuple_with_pos) == 3, f"{expected_type} should have 3 elements"
        assert tuple_with_pos[0] == expected_type
        assert isinstance(tuple_with_pos[2], dict)
        assert "start_line_no" in tuple_with_pos[2]
        assert "end_line_no" in tuple_with_pos[2]

    # Test with include_meta=False (default)
    tuple_without_pos = indent.to_tuple(include_meta=False)
    assert len(tuple_without_pos) == 2
    assert tuple_without_pos[0] == "indent"


def test_template_segment_to_tuple_with_position():
    """Test that TemplateSegment.to_tuple includes position when requested."""
    from sqlfluff.core.parser.segments.meta import TemplateSegment

    raw_sql = "SELECT 1"
    templated_file = TemplatedFile.from_string(raw_sql)

    # Create a TemplateSegment with position marker
    template_seg = TemplateSegment(
        pos_marker=PositionMarker(
            slice(0, 6),
            slice(0, 6),
            templated_file,
        ),
        source_str="SELECT",
        block_type="test_block",
    )

    # Test with include_meta=True
    tuple_with_pos = template_seg.to_tuple(include_meta=True)
    assert len(tuple_with_pos) == 3
    assert tuple_with_pos[0] == "placeholder"
    assert tuple_with_pos[1] == "SELECT"
    assert isinstance(tuple_with_pos[2], dict)
    assert "start_line_no" in tuple_with_pos[2]
