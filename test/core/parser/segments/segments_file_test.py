"""Test the BaseFileSegment class."""

import pytest

from sqlfluff.core.parser import BaseFileSegment


@pytest.fixture(scope="module")
def raw_seg_list(generate_test_segments):
    """Construct a list of raw segments as a fixture."""
    return generate_test_segments(["foobar", ".barfoo"])


def test__parser__base_segments_file(raw_seg_list):
    """Test BaseFileSegment to behave as expected."""
    base_seg = BaseFileSegment(raw_seg_list, fname="/some/dir/file.sql")
    assert base_seg.type == "file"
    assert base_seg.file_path == "/some/dir/file.sql"
    assert base_seg.can_start_end_non_code
    assert base_seg.allow_empty
