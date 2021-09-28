"""Tests for PositionMarker."""

import pytest

from sqlfluff.core.templaters import TemplatedFile
from sqlfluff.core.parser.markers import PositionMarker


@pytest.mark.parametrize(
    "raw,start_pos,end_pos",
    [
        ("fsaljk", (0, 0), (0, 6)),
        ("", (2, 2), (2, 2)),
        # NB: 1 indexed, not 0 indexed.
        ("\n", (2, 2), (3, 1)),
        ("boo\n", (2, 2), (3, 1)),
        ("boo\nfoo", (2, 2), (3, 4)),
        ("\nfoo", (2, 2), (3, 4)),
    ],
)
def test_markers__infer_next_position(raw, start_pos, end_pos):
    """Test that we can correctly infer positions from strings."""
    assert end_pos == PositionMarker.infer_next_position(raw, *start_pos)


def test_markers__setting_position_raw():
    """Test that we can correctly infer positions from strings & locations."""
    templ = TemplatedFile.from_string("foobar")
    # Check inference in the template
    assert templ.get_line_pos_of_char_pos(2, source=True) == (1, 3)
    assert templ.get_line_pos_of_char_pos(2, source=False) == (1, 3)
    # Now check it passes through
    pos = PositionMarker(slice(2, 5), slice(2, 5), templ)
    # Can we infer positions correctly?
    assert pos.working_loc == (1, 3)


def test_markers__setting_position_working():
    """Test that we can correctly set positions manually."""
    templ = TemplatedFile.from_string("foobar")
    pos = PositionMarker(slice(2, 5), slice(2, 5), templ, 4, 4)
    # Can we NOT infer when we're told.
    assert pos.working_loc == (4, 4)
