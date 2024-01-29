"""Tests for the raw_file_slices module."""

import pytest

from sqlfluff.core.templaters.base import RawFileSlice
from sqlfluff.utils.functional import raw_file_slices

rs_templated_abc = RawFileSlice("{{abc}}", "templated", 0)
rs_templated_def = RawFileSlice("{{def}}", "templated", 0)
rs_literal_abc = RawFileSlice("abc", "literal", 0)


@pytest.mark.parametrize(
    ["input", "expected"],
    [
        [
            raw_file_slices.RawFileSlices(rs_templated_abc, templated_file=None),
            True,
        ],
        [
            raw_file_slices.RawFileSlices(rs_templated_def, templated_file=None),
            False,
        ],
        [
            raw_file_slices.RawFileSlices(
                rs_templated_abc, rs_templated_def, templated_file=None
            ),
            False,
        ],
    ],
)
def test_slices_all(input, expected):
    """Test the "all()" function."""
    assert input.all(lambda s: "abc" in s.raw) == expected


@pytest.mark.parametrize(
    ["input", "expected"],
    [
        [
            raw_file_slices.RawFileSlices(rs_templated_abc, templated_file=None),
            True,
        ],
        [
            raw_file_slices.RawFileSlices(rs_templated_def, templated_file=None),
            False,
        ],
        [
            raw_file_slices.RawFileSlices(
                rs_templated_abc, rs_templated_def, templated_file=None
            ),
            True,
        ],
    ],
)
def test_slices_any(input, expected):
    """Test the "any()" function."""
    assert input.any(lambda s: "abc" in s.raw) == expected
