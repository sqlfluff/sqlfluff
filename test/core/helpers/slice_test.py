"""Test the slice helpers."""

import pytest

from sqlfluff.core.helpers.slice import slice_overlaps


@pytest.mark.parametrize(
    "s1,s2,result",
    [
        # Identity case
        (slice(0, 1), slice(0, 1), True),
        # Adjoining zero length slices aren't overlaps
        (slice(1, 1), slice(0, 1), False),
        (slice(0, 0), slice(0, 1), False),
        (slice(0, 1), slice(1, 1), False),
        (slice(0, 1), slice(0, 0), False),
        # Contained slices are overlaps
        (slice(0, 3), slice(1, 2), True),
        (slice(1, 2), slice(0, 3), True),
        # ...even if they're zero length
        (slice(0, 3), slice(1, 1), True),
        (slice(1, 1), slice(0, 3), True),
        # Easy cases of non-overlaps
        (slice(1, 2), slice(3, 4), False),
        (slice(3, 4), slice(1, 2), False),
        (slice(1, 2), slice(2, 3), False),
        (slice(2, 3), slice(1, 2), False),
        # Partial overlaps are overlaps
        (slice(1, 3), slice(2, 4), True),
        (slice(2, 4), slice(1, 3), True),
    ],
)
def test__parser__slice_overlaps_result(s1, s2, result):
    """Test _findall."""
    assert slice_overlaps(s1, s2) == result


@pytest.mark.parametrize(
    "s1,s2",
    [
        # Check None situations
        (slice(None, 1), slice(0, 1)),
        (slice(0, None), slice(0, 1)),
        (slice(0, 1), slice(None, 1)),
        (slice(0, 1), slice(0, None)),
        (slice(None, None), slice(None, None)),
        # Check positivity
        (slice(1, 0), slice(0, 1)),
        (slice(0, 1), slice(1, 0)),
    ],
)
def test__parser__slice_overlaps_error(s1, s2):
    """Test assertions of slice_overlaps."""
    with pytest.raises(AssertionError):
        slice_overlaps(s1, s2)
