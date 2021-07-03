"""Defines small container classes to hold intermediate results during linting."""

from typing import (
    List,
    NamedTuple,
    Optional,
    Tuple,
    Dict,
)

from sqlfluff.core.errors import SQLBaseError, SQLTemplaterError
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


class RenderedFile(NamedTuple):
    """An object to store the result of a templated file/string.

    This is notable as it's the intermediate state between what happens
    in the main process and the child processes when running in parallel mode.
    """

    templated_file: TemplatedFile
    templater_violations: List[SQLTemplaterError]
    config: FluffConfig
    time_dict: Dict[str, float]
    fname: str
    encoding: str


class ParsedString(NamedTuple):
    """An object to store the result of parsing a string.

    Args:
        `parsed` is a segment structure representing the parsed file. If
            parsing fails due to an unrecoverable violation then we will
            return None.
        `violations` is a :obj:`list` of violations so far, which will either be
            templating, lexing or parsing violations at this stage.
        `time_dict` is a :obj:`dict` containing timings for how long each step
            took in the process.
        `templated_file` is a :obj:`TemplatedFile` containing the details
            of the templated file.
    """

    tree: Optional[BaseSegment]
    violations: List[SQLBaseError]
    time_dict: dict
    templated_file: TemplatedFile
    config: FluffConfig
    fname: str


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
