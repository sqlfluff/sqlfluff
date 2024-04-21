"""Defines small container classes to hold intermediate results during linting."""

from typing import Any, Dict, List, NamedTuple, Optional, Tuple, Union

from sqlfluff.core.config import FluffConfig
from sqlfluff.core.errors import (
    SQLBaseError,
    SQLLexError,
    SQLParseError,
    SQLTemplaterError,
)
from sqlfluff.core.parser.segments.base import BaseSegment
from sqlfluff.core.templaters import TemplatedFile


class RuleTuple(NamedTuple):
    """Rule Tuple object for describing rules."""

    code: str
    name: str
    description: str
    groups: Tuple[str, ...]
    aliases: Tuple[str, ...]


class RenderedFile(NamedTuple):
    """An object to store the result of a templated file/string.

    This is notable as it's the intermediate state between what happens
    in the main process and the child processes when running in parallel mode.
    """

    templated_variants: List[TemplatedFile]
    templater_violations: List[SQLTemplaterError]
    config: FluffConfig
    time_dict: Dict[str, float]
    fname: str
    encoding: str
    source_str: str


class ParsedVariant(NamedTuple):
    """An object to store the result of parsing a single TemplatedFile.

    Args:
        `templated_file` is a :obj:`TemplatedFile` containing the details
            of the templated file. If templating fails, this will return None.
        `tree` is a segment structure representing the parsed file. If
            parsing fails due to an unrecoverable violation then we will
            return None.
        `violations` is a :obj:`list` of violations so far, which will either be
            lexing or parsing violations at this stage. Templated violations
            are stored in the ParsedString object.
    """

    templated_file: Optional[TemplatedFile]
    tree: Optional[BaseSegment]
    lexing_violations: List[SQLLexError]
    parsing_violations: List[SQLParseError]

    def violations(self) -> List[Union[SQLLexError, SQLParseError]]:
        """Returns the combined set of violations for this variant."""
        return [*self.lexing_violations, *self.parsing_violations]


class ParsedString(NamedTuple):
    """An object to store the result of parsing a string.

    Args:
        `tree` is a segment structure representing the parsed file. If
            parsing fails due to an unrecoverable violation then we will
            return None.
        `violations` is a :obj:`list` of violations so far, which will either be
            templating, lexing or parsing violations at this stage.
        `time_dict` is a :obj:`dict` containing timings for how long each step
            took in the process.
        `templated_file` is a :obj:`TemplatedFile` containing the details
            of the templated file. If templating fails, this will return None.
    """

    tree: Optional[BaseSegment]
    violations: List[SQLBaseError]
    time_dict: Dict[str, Any]
    templated_file: Optional[TemplatedFile]
    config: FluffConfig
    fname: str
    source_str: str
