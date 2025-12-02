"""Tests for the MatchResult class.

NOTE: This is all experimental for now.
"""

import pytest

from sqlfluff.core.parser.match_result import MatchResult
from sqlfluff.core.parser.segments import BaseSegment, Dedent, Indent


class ExampleSegment(BaseSegment):
    """A minimal example segment for testing."""

    type = "example"


def _recursive_assert_pos(segment):
    assert segment.pos_marker
    for seg in segment.segments:
        _recursive_assert_pos(seg)


@pytest.mark.parametrize(
    "segment_seed,match_result,match_len,serialised_result",
    [
        (
            ["a", "b", "c", "d", "e"],
            MatchResult(
                matched_slice=slice(1, 4),
                insert_segments=((3, Indent),),
                child_matches=(
                    MatchResult(
                        matched_slice=slice(2, 3),
                        matched_class=ExampleSegment,
                        insert_segments=((2, Indent),),
                    ),
                ),
            ),
            3,
            (
                ("raw", "b"),
                ("example", (("indent", ""), ("raw", "c"))),
                ("indent", ""),
                ("raw", "d"),
            ),
        ),
        (
            ["a", "b", "c", "d", "e"],
            MatchResult(
                matched_slice=slice(1, 4),
                insert_segments=((2, Dedent),),
            ),
            3,
            (
                ("raw", "b"),
                ("dedent", ""),
                ("raw", "c"),
                ("raw", "d"),
            ),
        ),
        (
            ["a"],
            MatchResult(
                # An example with only inserts.
                matched_slice=slice(0, 0),
                insert_segments=((0, Dedent),),
            ),
            0,
            (("dedent", ""),),
        ),
    ],
)
def test__parser__matchresult2_apply(
    segment_seed, match_result, match_len, serialised_result, generate_test_segments
):
    """Test MatchResult.apply().

    This includes testing instantiating the MatchResult and
    whether setting some attributes and not others works as
    expected.
    """
    input_segments = generate_test_segments(segment_seed)

    # Test the length attribute.
    # NOTE: It's not the number of segments we'll return, but the span
    # of the match in the original sequence.
    assert len(match_result) == match_len

    out_segments = match_result.apply(input_segments)
    serialised = tuple(
        seg.to_tuple(show_raw=True, include_meta=True) for seg in out_segments
    )
    assert serialised == serialised_result

    # Test that _every_ segment (including metas) has a position marker already.
    for seg in out_segments:
        _recursive_assert_pos(seg)
