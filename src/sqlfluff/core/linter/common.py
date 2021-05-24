"""Defines small container classes to hold intermediate results during linting."""

from typing import (
    List,
    NamedTuple,
    Optional,
    Tuple,
)

from sqlfluff.core.errors import SQLBaseError
from sqlfluff.core.templaters import TemplatedFile
from sqlfluff.core.config import FluffConfig
from sqlfluff.core.parser.segments.base import BaseSegment


class RuleTuple(NamedTuple):
    """Rule Tuple object for describing rules."""

    code: str
    description: str


class NoQaDirective(NamedTuple):
    """Parsed version of a 'noqa' comment."""

    line_no: int  # Source line number
    rules: Optional[Tuple[str, ...]]  # Affected rule names
    action: Optional[str]  # "enable", "disable", or "None"


class ParsedString(NamedTuple):
    """An object to store the result of parsing a string."""

    tree: Optional[BaseSegment]
    violations: List[SQLBaseError]
    time_dict: dict
    templated_file: TemplatedFile
    config: FluffConfig


class EnrichedFixPatch(NamedTuple):
    """An edit patch for a source file."""

    source_slice: slice
    templated_slice: slice
    fixed_raw: str
    # The patch category, functions mostly for debugging and explanation
    # than for function. It allows traceability of *why* this patch was
    # generated.
    patch_category: str
    templated_str: str
    source_str: str

    def dedupe_tuple(self):
        """Generate a tuple of this fix for deduping."""
        return (self.source_slice, self.fixed_raw)
