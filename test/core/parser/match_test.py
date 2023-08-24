"""Tests for the MatchResult2 class.

NOTE: This is all experimental for now.
"""

from sqlfluff.core.parser.segments import BaseSegment, Indent
from sqlfluff.core.parser.match_result import MatchResult2


class ExampleSegment(BaseSegment):
    """A minimal example segment for testing."""

    type = "example"


def test__parser__matchresult2_apply(generate_test_segments):
    """Test MatchResult2.apply().

    This includes testing instantiating the MatchResult2 and
    whether setting some attributes and not others works as
    expected.
    """
    input_segments = generate_test_segments(["a", "b", "c", "d", "e"])
    mr2 = MatchResult2(
        matched_slice=slice(1, 4),
        insert_segments=((3, Indent),),
        child_matches=(
            MatchResult2(
                matched_slice=slice(2, 3),
                matched_class=ExampleSegment,
                insert_segments=((2, Indent),),
            ),
        ),
    )

    out_segments = mr2.apply(input_segments)
    serialised = tuple(
        seg.to_tuple(show_raw=True, include_meta=True) for seg in out_segments
    )
    assert serialised == (
        ("raw", "b"),
        ("example", (("indent", ""), ("raw", "c"))),
        ("indent", ""),
        ("raw", "d"),
    )
