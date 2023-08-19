"""Tests for PositionMarker."""

import pytest

from sqlfluff.core.parser.markers import PositionMarker
from sqlfluff.core.templaters import TemplatedFile


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
    # Check other marker properties work too (i.e. source properties)
    assert pos.line_no == 1
    assert pos.line_pos == 3  # i.e. 2 + 1 (for 1-indexed)


def test_markers__setting_position_working():
    """Test that we can correctly set positions manually."""
    templ = TemplatedFile.from_string("foobar")
    pos = PositionMarker(slice(2, 5), slice(2, 5), templ, 4, 4)
    # Can we don't infer when we're explicitly told.
    assert pos.working_loc == (4, 4)


def test_markers__comparison():
    """Test that we can correctly compare markers."""
    templ = TemplatedFile.from_string("abc")
    # Make position markers for each of a, b & c
    # NOTE: We're not explicitly setting the working location, we
    # rely here on the marker inferring that correctly itself.
    a_pos = PositionMarker(slice(0, 1), slice(0, 1), templ)
    b_pos = PositionMarker(slice(1, 2), slice(1, 2), templ)
    c_pos = PositionMarker(slice(2, 3), slice(2, 3), templ)
    all_pos = (a_pos, b_pos, c_pos)
    # Check equality
    assert all(p == p for p in all_pos)
    # Check inequality
    assert a_pos != b_pos and a_pos != c_pos and b_pos != c_pos
    # Check less than
    assert a_pos < b_pos and b_pos < c_pos
    assert not c_pos < a_pos
    # Check greater than
    assert c_pos > a_pos and c_pos > b_pos
    assert not a_pos > c_pos
    # Check less than or equal
    assert all(a_pos <= p for p in all_pos)
    # Check greater than or equal
    assert all(c_pos >= p for p in all_pos)
