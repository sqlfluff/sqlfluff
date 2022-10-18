"""Methods for deducing and understanding indents."""

import logging

from sqlfluff.core.parser import RawSegment, BaseSegment


# We're in the utils module, but users will expect reflow
# logs to appear in the context of rules. Hence it's a subset
# of the rules logger.
reflow_logger = logging.getLogger("sqlfluff.rules.reflow")


def deduce_line_indent(raw_segment: RawSegment, root_segment: BaseSegment) -> str:
    """Given a raw segment, deduce the indent of it's line."""
    seg_idx = root_segment.raw_segments.index(raw_segment)
    indent_seg = None
    for seg in root_segment.raw_segments[seg_idx::-1]:
        if seg.is_code:
            indent_seg = None
        elif seg.is_type("whitespace"):
            indent_seg = seg
        elif seg.is_type("newline"):
            break
    reflow_logger.debug("Deduced indent for %s as %s", raw_segment, indent_seg)
    if indent_seg:
        return indent_seg.raw
    else:
        return ""
