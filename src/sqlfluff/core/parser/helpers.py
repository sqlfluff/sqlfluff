"""Helpers for the parser module."""

from typing import Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from .segments import BaseSegment


def frame_msg(msg: str) -> str:
    """Frame a message with hashes so that it covers five lines."""
    return "\n###\n#\n# {0}\n#\n###".format(msg)


def curtail_string(s: str, length=20) -> str:
    """Trim a string nicely to length."""
    if len(s) > length:
        return s[:length] + "..."
    else:
        return s


def join_segments_raw(segments: Tuple["BaseSegment", ...]) -> str:
    """Make a string from the joined `raw` attributes of an iterable of segments."""
    return "".join(s.raw for s in segments)


def join_segments_raw_curtailed(segments: Tuple["BaseSegment", ...], length=20) -> str:
    """Make a string up to a certain length from an iterable of segments."""
    return curtail_string(join_segments_raw(segments), length=length)


def check_still_complete(
    segments_in: Tuple["BaseSegment", ...],
    matched_segments: Tuple["BaseSegment", ...],
    unmatched_segments: Tuple["BaseSegment", ...],
) -> bool:
    """Check that the segments in are the same as the segments out."""
    initial_str = join_segments_raw(segments_in)
    current_str = join_segments_raw(matched_segments + unmatched_segments)
    if initial_str != current_str:
        raise RuntimeError(
            "Dropped elements in sequence matching! {0!r} != {1!r}".format(
                initial_str, current_str
            )
        )
    return True


def trim_non_code(segments: Tuple["BaseSegment", ...]):
    """Take segments and split off surrounding non-code segments as appropriate."""
    pre_buff: Tuple["BaseSegment", ...] = ()
    seg_buff: Tuple["BaseSegment", ...] = segments
    post_buff: Tuple["BaseSegment", ...] = ()

    if seg_buff:
        pre_buff = ()
        seg_buff = segments
        post_buff = ()

        # Trim the start
        while seg_buff and not seg_buff[0].is_code:
            pre_buff = pre_buff + (seg_buff[0],)
            seg_buff = seg_buff[1:]

        # Trim the end
        while seg_buff and not seg_buff[-1].is_code:
            post_buff = (seg_buff[-1],) + post_buff
            seg_buff = seg_buff[:-1]

    return pre_buff, seg_buff, post_buff
