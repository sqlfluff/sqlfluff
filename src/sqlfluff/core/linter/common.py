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
        templated_file (:obj:`TemplatedFile`): Containing the details
            of the templated file. If templating fails, this will be `None`.
        tree (:obj:`BaseSegment`): The segment structure representing the
            parsed file. If parsing fails due to an unrecoverable
            violation then we will be None.
        lexing_violations (:obj:`list` of :obj:`SQLLexError`): Any violations
            raised during the lexing phase.
        parsing_violations (:obj:`list` of :obj:`SQLParseError`): Any violations
            raised during the lexing phase.
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
        parsed_variants (:obj:`list` of :obj:`ParsedVariant`): The parsed
            variants of this file. Empty if parsing or templating failed.
        templating_violations (:obj:`list` of :obj:`SQLTemplaterError`):
            Any violations raised during the templating phase. Any violations
            raised during lexing or parsing can be found in the
            `parsed_variants`, or accessed using the `.violations()` method
            which combines all the violations.
        time_dict (:obj:`dict`): Contains timings for how long each step
            took in the process.
        config (:obj:`FluffConfig`): The active config for this file,
            including any parsed in-file directives.
        fname (str): The name of the file. Used mostly for user feedback.
        source_str (str): The raw content of the source file.
    """

    parsed_variants: List[ParsedVariant]
    templating_violations: List[SQLTemplaterError]
    time_dict: Dict[str, Any]
    config: FluffConfig
    fname: str
    source_str: str

    def violations(self) -> List[SQLBaseError]:
        """Returns the combined set of violations for this variant."""
        return [
            *self.templating_violations,
            *(v for variant in self.parsed_variants for v in variant.violations()),
        ]

    def root_variant(self) -> Optional[ParsedVariant]:
        """Returns the root variant if successfully parsed, otherwise None."""
        if not self.parsed_variants:
            return None
        root_variant = self.parsed_variants[0]
        if not root_variant.tree:
            return None
        return root_variant
