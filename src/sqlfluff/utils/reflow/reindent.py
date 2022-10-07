"""Methods for deducing and understanding indents."""

import logging
from typing import List
from dataclasses import dataclass

from sqlfluff.core.parser import RawSegment, BaseSegment
from sqlfluff.utils.reflow.elements import ReflowPoint, ReflowSequenceType


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


@dataclass
class _ReindentLine:
    start_point_idx: int
    end_point_idx: int
    initial_indent_balance: int
    current_indent: str


def map_reindent_lines(
    elements: ReflowSequenceType, initial_balance: int = 0
) -> List[_ReindentLine]:
    """Scan the sequence to map individual lines to indent."""
    init_idx = 0
    last_pt_idx = 0
    if elements and isinstance(elements[0], ReflowPoint):
        indent = elements[0].get_indent() or ""
    else:
        indent = ""
    indent_balance = initial_balance
    last_indent_balance = indent_balance
    result: List[_ReindentLine] = []
    for idx, elem in enumerate(elements):
        if isinstance(elem, ReflowPoint):
            last_pt_idx = idx
            indent_balance += elem.get_indent_impulse()
            # Have we found a newline?
            # We skip the trivial matches (mostly to avoid a wierd start).
            if "newline" in elem.class_types and idx != init_idx:
                result.append(_ReindentLine(init_idx, idx, last_indent_balance, indent))
                # Set the index and indent for next time
                indent = elem.get_indent() or ""
                init_idx = idx
                last_indent_balance = indent_balance
    # Do we have meaningful content at the end.
    # NOTE: we don't handle any indent before the end_of_file segment.
    # Which is why we use last_pt_idx not just len(elements).
    if last_pt_idx - init_idx > 1:
        result.append(_ReindentLine(init_idx, last_pt_idx, last_indent_balance, indent))

    return result
