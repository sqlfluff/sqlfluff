"""Test the BaseFileSegment class."""

from sqlfluff.core.parser import BaseFileSegment


def test__parser__base_segments_file(raw_segments):
    """Test BaseFileSegment to behave as expected."""
    base_seg = BaseFileSegment(raw_segments, fname="/some/dir/file.sql")
    assert base_seg.type == "file"
    assert base_seg.file_path == "/some/dir/file.sql"
    assert base_seg.can_start_end_non_code
    assert base_seg.allow_empty
