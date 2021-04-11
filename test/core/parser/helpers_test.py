"""Test the helpers."""

import pytest

from sqlfluff.core.parser.helpers import trim_non_code_segments, iter_indices


@pytest.mark.parametrize(
    "token_list,pre_len,mid_len,post_len",
    [
        (["bar", ".", "bar"], 0, 3, 0),
        (("bar", ".", "bar"), 0, 3, 0),
        ([], 0, 0, 0),
        (["  ", "\n", "\t", "bar", ".", "bar", "  ", "\n", "\t"], 3, 3, 3),
    ],
)
def test__parser__helper_trim_non_code_segments(
    token_list,
    pre_len,
    mid_len,
    post_len,
    generate_test_segments,
):
    """Test trim_non_code_segments."""
    seg_list = generate_test_segments(token_list)
    pre, mid, post = trim_non_code_segments(seg_list)
    # Assert lengths
    assert (len(pre), len(mid), len(post)) == (pre_len, mid_len, post_len)
    # Assert content
    assert [elem.raw for elem in pre] == list(token_list[:pre_len])
    assert [elem.raw for elem in mid] == list(token_list[pre_len : pre_len + mid_len])
    assert [elem.raw for elem in post] == list(token_list[len(seg_list) - post_len :])


@pytest.mark.parametrize(
    "seq,val,indices",
    [
        ([], 1, []),
        ([0, 1, 0], 2, []),
        ([0, 1, 0], 1, [1]),
        ([0, 1, 0], 0, [0, 2]),
    ],
)
def test__parser__helper_iter_indices(seq, val, indices):
    """Test iter_indices."""
    res = list(iter_indices(seq, val))
    assert res == indices
