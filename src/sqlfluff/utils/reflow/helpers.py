"""Helper utilities for reflow."""

from itertools import chain
from typing import Iterable, List

from sqlfluff.core.rules.base import LintFix, LintResult
from sqlfluff.core.parser import BaseSegment


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
