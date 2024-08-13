"""Helpers for the parser module."""

from typing import TYPE_CHECKING, Tuple

from sqlfluff.core.errors import SQLParseError

if TYPE_CHECKING:
    from sqlfluff.core.parser.segments import BaseSegment  # pragma: no cover


def join_segments_raw(segments: Tuple["BaseSegment", ...]) -> str:
    """Make a string from the joined `raw` attributes of an iterable of segments."""
    return "".join(s.raw for s in segments)


def check_still_complete(
    segments_in: Tuple["BaseSegment", ...],
    matched_segments: Tuple["BaseSegment", ...],
    unmatched_segments: Tuple["BaseSegment", ...],
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
    segments: Tuple["BaseSegment", ...]
) -> Tuple[
    Tuple["BaseSegment", ...], Tuple["BaseSegment", ...], Tuple["BaseSegment", ...]
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
