"""Python wrapper for Rust parser that returns BaseSegment trees.

This module provides RustParser, a drop-in replacement for the Python Parser
that uses the Rust implementation under the hood but returns Python BaseSegment
objects for compatibility with the linter infrastructure.

The Rust parser returns a MatchResult that describes what was matched (slices,
classes, inserts) without building the AST. Python's MatchResult.apply() then
constructs the BaseSegment tree, leveraging proven logic and avoiding
double-counting issues.
"""

import functools
import logging
from typing import TYPE_CHECKING, Any, Optional

from sqlfluff.core.config import FluffConfig
from sqlfluff.core.errors import SQLParseError
from sqlfluff.core.parser.match_result import MatchResult
from sqlfluff.core.parser.segments import (
    BaseFileSegment,
    BaseSegment,
    Dedent,
    ImplicitIndent,
    Indent,
    TemplateSegment,
    UnparsableSegment,
)

if TYPE_CHECKING:  # pragma: no cover
    from sqlfluff.core.dialects.base import Dialect

# Instantiate the parser logger
parser_logger = logging.getLogger("sqlfluff.parser")


try:
    from sqlfluffrs import RsMatchResult, RsParseError, RsParser, RsToken

    _HAS_RUST_PARSER = True

    class RustParser:
        """Parser wrapper that uses Rust implementation but returns BaseSegment.

        This is designed to be a drop-in replacement for the Python Parser class,
        with the same interface but using the faster Rust parser internally.

        Example:
            >>> from sqlfluff.core.parser import RustParser
            >>> parser = RustParser(dialect="ansi")
            >>> segment = parser.parse(tokens, fname="test.sql")
        """

        def __init__(
            self,
            config: Optional["FluffConfig"] = None,
            dialect: Optional[str] = None,
        ) -> None:
            """Initialize the Rust parser with config or dialect.

            Args:
                config: FluffConfig instance (takes precedence over dialect)
                dialect: Dialect name (used if config not provided)

            Raises:
                ValueError: If both config and dialect are provided
            """
            if config and dialect:
                raise ValueError(  # pragma: no cover
                    "RustParser does not support setting both `config` and `dialect`."
                )

            # Use the provided config or create one from the dialect.
            self.config = config or FluffConfig.from_kwargs(dialect=dialect)
            self.RootSegment: type[BaseFileSegment] = self.config.get(
                "dialect_obj"
            ).get_root_segment()

            # Extract indentation config and convert boolean values only
            indent_config = self.config.get_section("indentation") or {}
            if indent_config:
                # Only keep boolean config values for conditional evaluation
                # Non-boolean values like "indent_unit": "space" are not needed
                # for conditionals
                indent_config = {
                    k: v for k, v in indent_config.items() if isinstance(v, bool)
                }

            # Create the Rust parser
            self._rs_parser = RsParser(
                dialect=self.config.get("dialect"), indent_config=indent_config
            )

        def parse(
            self,
            segments: tuple["BaseSegment", ...],
            fname: Optional[str] = None,
            parse_statistics: bool = False,
        ) -> Optional["BaseSegment"]:
            """Parse a series of lexed tokens using the Rust parser.

            This method now uses the MatchResult-based approach where Rust returns
            a MatchResult and Python's apply() builds the AST, avoiding double-counting.

            Args:
                segments: Tuple of RawSegment objects from the lexer
                fname: Optional filename for error reporting
                parse_statistics: Whether to log parse statistics (not yet implemented)
                tf: Optional TemplatedFile for position marker reconstruction

            Returns:
                BaseSegment tree representing the parsed SQL, or None if empty

            Note:
                The segments parameter contains RawSegment objects that were created
                from RsToken objects using RawSegment.from_rstoken(). To optimize,
                we need to extract the original RsToken objects to pass to the Rust
                parser directly.
            """
            if not segments:  # pragma: no cover
                return None

            # PYTHON PARITY: Trim non-code from start (like root_parse)
            _start_idx = 0
            for _start_idx in range(len(segments)):
                if segments[_start_idx].is_code:
                    break

            # PYTHON PARITY: Trim non-code from end (like root_parse)
            _end_idx = len(segments)
            for _end_idx in range(len(segments), _start_idx - 1, -1):
                if segments[_end_idx - 1].is_code:
                    break

            if _start_idx == _end_idx:
                # No code segments - return FileSegment with just non-code
                return self.RootSegment(segments=segments, fname=fname)

            # Extract the original RsToken objects from the RawSegments
            # PYTHON PARITY: Only parse the code portion (segments[_start_idx:_end_idx])
            # Just like Python's match(segments[:_end_idx], _start_idx, ...)
            tokens = self._extract_tokens_from_segments(segments[_start_idx:_end_idx])

            # Parse using Rust parser to get MatchResult
            # The Rust parser may raise RsParseError for certain parse errors (e.g.,
            # missing closing brackets in terminators). We catch these and convert to
            # SQLParseError. Regular parse errors are embedded in the MatchResult.
            try:
                rs_match = self._rs_parser.parse_match_result_from_tokens(tokens)
            except RsParseError as e:
                # Convert Rust parse error to SQLParseError with position info
                raise SQLParseError.from_rs_parse_error(
                    e, segments[_start_idx:_end_idx]
                ) from e

            # Convert RsMatchResult to Python MatchResult
            # This also checks for embedded parse errors and raises them
            match = self._convert_rs_match_result(
                rs_match, segments[_start_idx:_end_idx]
            )
            parser_logger.info("Root Match:\n%s", match.stringify())

            # Apply the match result to construct the BaseSegment tree
            # PYTHON PARITY: Pass only the code portion (segments[_start_idx:_end_idx])
            # because match result indices are relative to this trimmed array
            _matched = match.apply(segments[_start_idx:_end_idx])

            # PYTHON PARITY: Add back any unmatched segments after the match
            # (relative to the _start_idx:_end_idx range)
            matched_stop = _start_idx + match.matched_slice.stop
            _unmatched = segments[matched_stop:_end_idx]

            # PYTHON PARITY: If there are unmatched code segments, wrap them in
            # UnparsableSegment. This matches the logic in FileSegment.root_parse()
            content: tuple[BaseSegment, ...]
            if not match:
                content = (
                    UnparsableSegment(
                        segments[_start_idx:_end_idx],
                        expected=str(self.RootSegment.match_grammar),
                    ),
                )
            elif _unmatched:
                _idx = 0
                for idx, seg in enumerate(_unmatched):
                    if seg.is_code:
                        _idx = idx
                        break
                else:  # pragma: no cover
                    _idx = len(_unmatched)
                content = (
                    _matched
                    + _unmatched[:_idx]
                    + (
                        UnparsableSegment(
                            _unmatched[_idx:], expected="Nothing else in FileSegment."
                        ),
                    )
                )
            else:
                content = _matched + _unmatched

            result = self.RootSegment(
                segments[:_start_idx] + content + segments[_end_idx:], fname=fname
            )

            if parse_statistics:  # pragma: no cover
                print("Warning: parse_statistics not yet implemented for Rust parser")

            return result

        @functools.lru_cache(maxsize=128)
        def _get_segment_class_by_name(
            self, segment_name: str
        ) -> Optional[type[BaseSegment]]:
            """Get a segment class by its exact class name from the dialect.

            Args:
                segment_name: The segment CLASS name (e.g., "AsAliasOperatorSegment")

            Returns:
                The segment class, or None if not found or is a grammar

            Note:
                Results are cached per parser instance since dialect is fixed.
            """
            if segment_name == "UnparsableSegment":
                return UnparsableSegment

            # Get the item from the dialect library
            dialect: Dialect = self.config.get("dialect_obj")
            item = dialect.get_segment(segment_name)

            # Verify it's a valid segment class (not a grammar element)
            if (
                item is not None
                and isinstance(item, type)
                and issubclass(item, BaseSegment)
            ):
                return item

            # Not a valid segment class - return None for grammar names
            return None  # pragma: no cover

        def _convert_rs_match_result(
            self,
            rs_match: "RsMatchResult",
            segments: tuple["BaseSegment", ...],
            depth: int = 0,
        ) -> MatchResult:
            """Convert Rust MatchResult to Python MatchResult.

            Args:
                rs_match: RsMatchResult from Rust parser
                segments: Segment array for error reporting
                depth: Current recursion depth for debugging

            Returns:
                Python MatchResult with equivalent structure

            """
            # Get the matched slice
            start, stop = rs_match.matched_slice
            matched_slice = slice(start, stop)

            # Convert child matches recursively
            # Pre-allocate list size for efficiency
            child_matches = (
                tuple(
                    self._convert_rs_match_result(child, segments, depth + 1)
                    for child in rs_match.child_matches
                )
                if rs_match.child_matches
                else ()
            )

            # Determine matched_class
            # The Rust parser now includes actual Python class names (from codegen)
            # in matched_class, so we can use them directly without conversion.
            matched_class: type["BaseSegment"] | None = (
                self._get_segment_class_by_name(rs_match.matched_class)
                if rs_match.matched_class
                else None
            )

            # Build segment_kwargs - optimize by checking first if we need any
            segment_kwargs: dict[str, Any] = {}
            if rs_match.instance_types:
                segment_kwargs["instance_types"] = tuple(rs_match.instance_types)

            # Copy over any segment_kwargs from Rust
            # (e.g., "expected" for UnparsableSegment)
            if rs_match.segment_kwargs:
                segment_kwargs.update(rs_match.segment_kwargs)

            # Set trim_chars from the match result if available
            if rs_match.trim_chars:
                segment_kwargs["trim_chars"] = tuple(rs_match.trim_chars)

            # Set casefold from the match result if available
            if rs_match.casefold:
                if rs_match.casefold == "upper":
                    segment_kwargs["casefold"] = str.upper
                elif rs_match.casefold == "lower":
                    segment_kwargs["casefold"] = str.lower

            # Set quoted_value and escape_replacement for normalization
            if rs_match.quoted_value:  # pragma: no cover
                segment_kwargs["quoted_value"] = rs_match.quoted_value
            if rs_match.escape_replacement:  # pragma: no cover
                segment_kwargs["escape_replacements"] = [rs_match.escape_replacement]

            # Extract insert_segments (Indent/Dedent meta segments)
            insert_segments: tuple[tuple[int, type], ...] = ()
            if rs_match.insert_segments:
                # rs_match.insert_segments now contains
                # (idx, seg_type, is_implicit) tuples
                insert_segments = tuple(
                    (
                        idx,
                        (
                            ImplicitIndent
                            if (seg_type == "indent" and is_implicit)
                            else (Indent if seg_type == "indent" else Dedent)
                        ),
                    )
                    for idx, seg_type, is_implicit in rs_match.insert_segments
                )

            return MatchResult(
                matched_slice=matched_slice,
                matched_class=matched_class,
                child_matches=child_matches,
                segment_kwargs=segment_kwargs,
                insert_segments=insert_segments,
            )

        @staticmethod
        def _template_segment_to_rstoken(segment: TemplateSegment) -> "RsToken":
            """Convert a Python TemplateSegment to a Rust RsToken.

            Creates a template placeholder token with the segment's metadata.
            This allows the Rust parser to handle templated SQL (Jinja, dbt, etc.).

            Args:
                segment: Python TemplateSegment from the lexer

            Returns:
                RsToken representing a template placeholder
            """
            # Extract position marker data
            pm = segment.pos_marker
            source_slice = (pm.source_slice.start, pm.source_slice.stop)
            templated_slice = (pm.templated_slice.start, pm.templated_slice.stop)
            templated_file = pm.templated_file

            # Convert block_uuid to hex string if present
            block_uuid_str = segment.block_uuid.hex if segment.block_uuid else None

            # Create template placeholder token using Rust constructor
            return RsToken.template_placeholder_from_slice(
                source_slice=source_slice,
                templated_slice=templated_slice,
                block_type=segment.block_type,
                _source_str=segment.source_str,  # Passed for API compatibility
                block_uuid=block_uuid_str,
                templated_file=templated_file,
            )

        def _extract_tokens_from_segments(
            self, segments: tuple["BaseSegment", ...]
        ) -> list["RsToken"]:
            """Extract RsToken objects from RawSegments.

            This extracts the cached _rstoken attribute from segments that came from
            the Rust lexer, or converts TemplateSegments to template placeholder tokens.

            Args:
                segments: Tuple of BaseSegment objects

            Returns:
                List of RsToken objects (or compatible token objects)
            """
            tokens = []
            for segment in segments:
                # Check if segment has _rstoken attribute (cached original token)
                if hasattr(segment, "_rstoken"):
                    tokens.append(segment._rstoken)
                elif isinstance(segment, TemplateSegment):
                    # Template segment - create template placeholder token
                    tokens.append(self._template_segment_to_rstoken(segment))
                else:  # pragma: no cover
                    # Cannot reconstruct RsToken from Python segment
                    raise ValueError(
                        f"Cannot extract RsToken from segment {segment!r}. "
                        f"Unsupported segment type: {type(segment).__name__}."
                    )

            return tokens

except ImportError:
    RustParser = None  # type: ignore[assignment, misc]
    _HAS_RUST_PARSER = False
