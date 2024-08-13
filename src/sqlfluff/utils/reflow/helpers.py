"""Helper utilities for reflow."""

import logging
from itertools import chain
from typing import Iterable, List

from sqlfluff.core.parser import BaseSegment, RawSegment
from sqlfluff.core.rules import LintFix, LintResult

# We're in the utils module, but users will expect reflow
# logs to appear in the context of rules. Hence it's a subset
# of the rules logger.
reflow_logger = logging.getLogger("sqlfluff.rules.reflow")


def fixes_from_results(results: Iterable[LintResult]) -> List[LintFix]:
    """Return a list of fixes from an iterable of LintResult."""
    return list(chain.from_iterable(result.fixes for result in results))


def pretty_segment_name(segment: BaseSegment) -> str:
    """Get a nicely formatted name of the segment."""
    if segment.is_type("symbol"):
        # In a symbol reference, show the raw value and type.
        # (With underscores as spaces)
        return segment.get_type().replace("_", " ") + f" {segment.raw!r}"
    elif segment.is_type("keyword"):
        # Reference keywords as keywords.
        return f"{segment.raw!r} keyword"
    else:
        # Reference other segments just by their type.
        # (With underscores as spaces)
        return segment.get_type().replace("_", " ")


def deduce_line_indent(raw_segment: RawSegment, root_segment: BaseSegment) -> str:
    """Given a raw segment, deduce the indent of its line."""
    seg_idx = root_segment.raw_segments.index(raw_segment)
    indent_seg = None
    # Use range and a lookup here because it's more efficient than slicing
    # as we only need a subset of the long series.
    for idx in range(seg_idx, -1, -1):
        seg = root_segment.raw_segments[idx]
        if seg.is_code:
            indent_seg = None
        elif seg.is_type("whitespace"):
            indent_seg = seg
        elif seg.is_type("newline"):
            break
    reflow_logger.debug("Deduced indent for %s as %s", raw_segment, indent_seg)
    return indent_seg.raw if indent_seg else ""
