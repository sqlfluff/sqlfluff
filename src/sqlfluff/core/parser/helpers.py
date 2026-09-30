"""Helpers for the parser module."""

from typing import TYPE_CHECKING

from sqlfluff.core.errors import SQLParseError
from sqlfluff.core.helpers.slice import is_zero_slice

if TYPE_CHECKING:
    from sqlfluff.core.parser.segments import BaseSegment  # pragma: no cover


def join_segments_raw(segments: tuple["BaseSegment", ...]) -> str:
    """Make a string from the joined `raw` attributes of an iterable of segments."""
    return "".join(s.raw for s in segments)


def check_still_complete(
    segments_in: tuple["BaseSegment", ...],
    matched_segments: tuple["BaseSegment", ...],
    unmatched_segments: tuple["BaseSegment", ...],
) -> bool:
    """Check that the segments in are the same as the segments out."""
    initial_str = join_segments_raw(segments_in)
    current_str = join_segments_raw(matched_segments + unmatched_segments)

    if initial_str != current_str:  # pragma: no cover
        segment = unmatched_segments[0] if unmatched_segments else None
        raise SQLParseError(
            f"Parse completeness check fail: {current_str!r} != {initial_str!r}",
            segment=segment,
        )
    return True


def trim_non_code_segments(
    segments: tuple["BaseSegment", ...],
) -> tuple[
    tuple["BaseSegment", ...], tuple["BaseSegment", ...], tuple["BaseSegment", ...]
]:
    """Take segments and split off surrounding non-code segments as appropriate.

    We use slices to avoid creating too many unnecessary tuples.
    """
    pre_idx = 0
    seg_len = len(segments)
    post_idx = seg_len

    if segments:
        seg_len = len(segments)

        # Trim the start
        while pre_idx < seg_len and not segments[pre_idx].is_code:
            pre_idx += 1

        # Trim the end
        while post_idx > pre_idx and not segments[post_idx - 1].is_code:
            post_idx -= 1

    return segments[:pre_idx], segments[pre_idx:post_idx], segments[post_idx:]


def is_inside_next_segment(segments: tuple["BaseSegment", ...], idx: int) -> bool:
    """Check whether the zero-length segment at `idx` sits inside a later sibling.

    When a lexed token spans a template tag (e.g. `b{% if x %}c{% endif %}`),
    the lexer yields the placeholder for the tag, and any indent or dedent
    for it, *before* that token. Their templated position is then after the
    start of the token. Any fix position or patch which uses that position
    as an end point covers the start of the token and deletes it.
    See: https://github.com/sqlfluff/sqlfluff/issues/8611
    """
    pos_marker = segments[idx].pos_marker
    # A new segment has no position yet, so it is not inside anything.
    if not pos_marker or not is_zero_slice(pos_marker.templated_slice):
        return False
    for next_seg in segments[idx + 1 :]:
        next_pos = next_seg.pos_marker
        if next_pos and not is_zero_slice(next_pos.templated_slice):
            is_inside: bool = (
                next_pos.templated_slice.start < pos_marker.templated_slice.start
            )
            return is_inside
    return False
