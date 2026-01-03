"""Python wrapper for Rust parser that returns BaseSegment trees.

This module provides RustParser, a drop-in replacement for the Python Parser
that uses the Rust implementation under the hood but returns Python BaseSegment
objects for compatibility with the linter infrastructure.

The Rust parser returns a MatchResult that describes what was matched (slices,
classes, inserts) without building the AST. Python's MatchResult.apply() then
constructs the BaseSegment tree, leveraging proven logic and avoiding
double-counting issues.
"""

from typing import TYPE_CHECKING, Optional

from sqlfluff.core.parser.match_result import MatchResult
from sqlfluff.core.parser.rsparser_adapter import get_segment_class_by_name
from sqlfluff.core.parser.segments.meta import TemplateSegment

if TYPE_CHECKING:  # pragma: no cover
    from sqlfluff.core.config import FluffConfig
    from sqlfluff.core.parser.segments import BaseSegment
    from sqlfluff.core.templaters.base import TemplatedFile
    from sqlfluffrs import RsMatchResult, RsToken


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
            raise ValueError(
                "RustParser does not support setting both `config` and `dialect`."
            )

        from sqlfluff.core.config import FluffConfig

        # Use the provided config or create one from the dialect.
        self.config = config or FluffConfig.from_kwargs(dialect=dialect)

        # Import here to avoid circular dependencies
        from sqlfluffrs import RsParser

        # Extract indentation config and convert boolean values only
        indent_config = self.config.get_section("indentation") or {}
        if indent_config:
            # Only keep boolean config values for conditional evaluation
            # Non-boolean values like "indent_unit": "space" are not needed for conditionals
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
        tf: Optional["TemplatedFile"] = None,
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
        # Use the new MatchResult-based implementation
        return self.parse_with_match_result(segments, fname, parse_statistics, tf)

    def parse_with_match_result(
        self,
        segments: tuple["BaseSegment", ...],
        fname: Optional[str] = None,
        parse_statistics: bool = False,
        tf: Optional["TemplatedFile"] = None,
    ) -> Optional["BaseSegment"]:
        """Parse using Rust MatchResult and Python's apply() logic.

        This method uses the new MatchResult-based approach where:
        1. Rust parser returns a MatchResult describing what matched
        2. Python's MatchResult.apply() builds the BaseSegment tree

        This follows the same pattern as Python's root_parse():
        - Trims non-code segments from start and end before parsing
        - Adds them back after parsing to preserve all tokens

        Args:
            segments: Tuple of RawSegment objects from the lexer
            fname: Optional filename for error reporting
            parse_statistics: Whether to log parse statistics
            tf: Optional TemplatedFile for position marker reconstruction

        Returns:
            BaseSegment tree representing the parsed SQL, or None if empty
        """
        if not segments:
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
            dialect = self.config.get("dialect_obj")
            file_segment_cls = dialect.get_segment("FileSegment")
            return file_segment_cls(segments=segments, fname=fname)

        # Extract templated_file from first segment if not provided
        if tf is None and segments:
            first_seg = segments[0]
            if hasattr(first_seg, "pos_marker") and first_seg.pos_marker:
                tf = first_seg.pos_marker.templated_file

        # Extract the original RsToken objects from the RawSegments
        # PYTHON PARITY: Only parse the code portion (segments[_start_idx:_end_idx])
        # Just like Python's match(segments[:_end_idx], _start_idx, ...)
        tokens = self._extract_tokens_from_segments(segments[_start_idx:_end_idx])

        # Parse using Rust parser to get MatchResult
        try:
            rs_match_result = self._rs_parser.parse_match_result_from_tokens(tokens)
        except Exception as e:
            # Check if this is a parse error that should be raised
            error_str = str(e)
            if "Couldn't find closing bracket" in error_str:
                # Re-raise as SQLParseError with proper location
                from sqlfluff.core.errors import SQLParseError

                # Try to find a meaningful segment for error location
                # Look for any start_bracket in the segments
                error_segment = None
                for seg in segments[_start_idx:_end_idx]:
                    if hasattr(seg, "is_type") and seg.is_type("start_bracket"):
                        error_segment = seg
                if error_segment is None and segments[_start_idx:_end_idx]:
                    # Fall back to first segment
                    error_segment = segments[_start_idx]
                raise SQLParseError(
                    error_str,
                    segment=error_segment,
                ) from e
            # Log other errors and return None (like Python parser does)
            print(f"Rust parser error: {e}")
            return None

        # Convert RsMatchResult to Python MatchResult
        # This also extracts any parse errors
        py_match_result, parse_errors = self._convert_rs_match_result(rs_match_result)

        # Check for parse errors and raise the first one
        # (Python parser would have raised during parsing)
        if parse_errors:
            error_msg, error_pos = parse_errors[0]
            # Get the segment at error position for its position marker
            if error_pos < len(segments[_start_idx:_end_idx]):
                error_segment = segments[_start_idx + error_pos]
                if hasattr(error_segment, "pos_marker") and error_segment.pos_marker:
                    from sqlfluff.core.errors import SQLParseError

                    raise SQLParseError(
                        error_msg,
                        segment=error_segment,
                    )

        # Apply the match result to construct the BaseSegment tree
        # PYTHON PARITY: Pass only the code portion (segments[_start_idx:_end_idx])
        # because match result indices are relative to this trimmed array
        result_segments = py_match_result.apply(segments[_start_idx:_end_idx])

        # PYTHON PARITY: Add back any unmatched segments after the match
        # (relative to the _start_idx:_end_idx range)
        _unmatched = segments[
            _start_idx + py_match_result.matched_slice.stop : _end_idx
        ]

        # PYTHON PARITY: If there are unmatched code segments, wrap them in UnparsableSegment
        # This matches the logic in FileSegment.root_parse() lines 98-111
        if _unmatched:
            # Find the first code segment in unmatched
            _first_code_idx = 0
            for _first_code_idx in range(len(_unmatched)):
                if _unmatched[_first_code_idx].is_code:
                    break

            # If we found code segments, create an UnparsableSegment
            if (
                _first_code_idx < len(_unmatched)
                and _unmatched[_first_code_idx].is_code
            ):
                from sqlfluff.core.parser.segments.base import UnparsableSegment

                unparsable = UnparsableSegment(
                    _unmatched[_first_code_idx:],
                    expected="Nothing else in FileSegment.",
                )
                content = result_segments + _unmatched[:_first_code_idx] + (unparsable,)
            else:
                # No code segments in unmatched, just add them as-is
                content = result_segments + _unmatched
        else:
            content = result_segments + _unmatched

        # Wrap in FileSegment following root_parse pattern
        dialect = self.config.get("dialect_obj")
        file_segment_cls = dialect.get_segment("FileSegment")

        # PYTHON PARITY: Reassemble with leading non-code + content + trailing non-code
        final_segments = segments[:_start_idx] + content + segments[_end_idx:]

        result = file_segment_cls(segments=final_segments, fname=fname)

        # PYTHON PARITY: Post-process to wrap unparsed brackets in UnparsableSegment
        # This handles cases where brackets appear as raw CodeSegments inside expressions
        result = self._wrap_unparsed_brackets(result)

        if parse_statistics:
            print("Warning: parse_statistics not yet implemented for Rust parser")

        return result

    def _wrap_unparsed_brackets(self, segment: "BaseSegment") -> "BaseSegment":
        """Post-process parsed tree to wrap unparsed brackets in UnparsableSegment.

        This handles cases where opening brackets without matching closing brackets
        appear as raw CodeSegments inside parsed expressions.
        """
        from sqlfluff.core.parser.segments.base import UnparsableSegment

        # Recursively process children
        if not hasattr(segment, "segments") or not segment.segments:
            return segment

        new_segments = []
        i = 0
        modified = False
        while i < len(segment.segments):
            child = segment.segments[i]

            # Check if this is an unparsed opening bracket
            # CodeSegment is the raw segment type, check by class name
            if (
                type(child).__name__ == "CodeSegment"
                and child.raw in ("(", "[", "{")
                and child.is_code
            ):
                # This is an unparsed bracket - wrap it and following tokens in UnparsableSegment
                # Find all tokens until we hit a non-code or reach end
                unparsable_segments = [child]
                i += 1
                while i < len(segment.segments):
                    next_seg = segment.segments[i]
                    if not next_seg.is_code:
                        break
                    unparsable_segments.append(next_seg)
                    i += 1

                # Create UnparsableSegment
                unparsable = UnparsableSegment(
                    tuple(unparsable_segments),
                    expected=f"Closing bracket for '{child.raw}'",
                )
                new_segments.append(unparsable)
                modified = True
            else:
                # Recursively process this child
                processed_child = self._wrap_unparsed_brackets(child)
                new_segments.append(processed_child)
                # Check if child was modified (different object)
                if processed_child is not child:
                    modified = True
                i += 1

        # Return a new segment with updated children if any changed
        if modified:
            # Different segment types have different constructor signatures.
            # Handle special cases that don't accept uuid parameter.
            seg_type_name = type(segment).__name__

            if seg_type_name == "FileSegment":
                # FileSegment(segments, pos_marker, fname)
                return segment.__class__(
                    segments=tuple(new_segments),
                    pos_marker=segment.pos_marker,
                    fname=getattr(segment, "fname", None),
                )
            elif seg_type_name == "UnparsableSegment":
                # UnparsableSegment(segments, pos_marker, expected)
                return segment.__class__(
                    segments=tuple(new_segments),
                    pos_marker=segment.pos_marker,
                    expected=getattr(segment, "_expected", ""),
                )
            elif seg_type_name == "BracketedSegment":
                # BracketedSegment requires start_bracket and end_bracket
                return segment.__class__(
                    segments=tuple(new_segments),
                    start_bracket=segment.start_bracket,
                    end_bracket=segment.end_bracket,
                    pos_marker=segment.pos_marker,
                    uuid=segment.uuid,
                )
            elif seg_type_name in (
                "RawSegment",
                "MetaSegment",
                "Indent",
                "Dedent",
                "TemplateSegment",
                "ImplicitIndent",
            ):
                # These segments don't have children, so they shouldn't reach here.
                # If they do, just return the original segment.
                return segment
            else:
                # Standard BaseSegment constructor: (segments, pos_marker, uuid)
                return segment.__class__(
                    segments=tuple(new_segments),
                    pos_marker=segment.pos_marker,
                    uuid=segment.uuid,
                )
        return segment

    def _convert_rs_match_result(
        self, rs_match: "RsMatchResult", depth: int = 0
    ) -> tuple[MatchResult, list[tuple[str, int]]]:
        """Convert Rust MatchResult to Python MatchResult.

        Args:
            rs_match: RsMatchResult from Rust parser
            depth: Current recursion depth for debugging

        Returns:
            Tuple of (Python MatchResult with equivalent structure, list of parse errors)
            Parse errors are tuples of (error_message, token_position)
        """
        # Collect parse errors from this match and all children
        parse_errors = []

        # Check if this match has a parse error
        if hasattr(rs_match, "parse_error") and rs_match.parse_error:
            parse_errors.append(rs_match.parse_error)

        # Get the matched slice
        start, stop = rs_match.matched_slice
        matched_slice = slice(start, stop)

        # Convert child matches recursively and collect their errors
        child_matches_list = []
        for child in rs_match.child_matches:
            child_match, child_errors = self._convert_rs_match_result(child, depth + 1)
            child_matches_list.append(child_match)
            parse_errors.extend(child_errors)

        child_matches = tuple(child_matches_list)

        # Determine matched_class
        # The Rust parser now includes actual Python class names (from codegen)
        # in matched_class, so we can use them directly without conversion.
        matched_class = None
        if rs_match.matched_class:
            # Handle core segment classes that aren't in the dialect library
            if rs_match.matched_class == "UnparsableSegment":
                from sqlfluff.core.parser.segments.base import UnparsableSegment

                matched_class = UnparsableSegment
            else:
                try:
                    # Try direct lookup first (exact class name from Rust codegen)
                    matched_class = get_segment_class_by_name(
                        rs_match.matched_class, self.config.get("dialect_obj")
                    )
                except (ValueError, KeyError):
                    # Grammar names or unknown classes - these are intermediate wrappers
                    # that don't need to be resolved to segment classes
                    matched_class = None

        # Build segment_kwargs from instance_types if present
        segment_kwargs = {}
        if rs_match.instance_types:
            segment_kwargs["instance_types"] = tuple(rs_match.instance_types)

        # Copy over any segment_kwargs from Rust (e.g., "expected" for UnparsableSegment)
        if rs_match.segment_kwargs:
            segment_kwargs.update(rs_match.segment_kwargs)

        # Set trim_chars from the match result if available
        if rs_match.trim_chars:
            segment_kwargs["trim_chars"] = tuple(rs_match.trim_chars)

        # Set casefold from the match result if available (dialect-specific from parser)
        if rs_match.casefold:
            if rs_match.casefold == "upper":
                segment_kwargs["casefold"] = str.upper
            elif rs_match.casefold == "lower":
                segment_kwargs["casefold"] = str.lower

        # Set quoted_value and escape_replacement for identifier/literal normalization
        if rs_match.quoted_value:
            segment_kwargs["quoted_value"] = rs_match.quoted_value
        if rs_match.escape_replacement:
            segment_kwargs["escape_replacements"] = [rs_match.escape_replacement]

        # Extract insert_segments (Indent/Dedent meta segments)
        insert_segments = ()
        if rs_match.insert_segments:
            from sqlfluff.core.parser.segments.meta import (
                Indent,
                Dedent,
                ImplicitIndent,
            )

            # rs_match.insert_segments now contains (idx, seg_type, is_implicit) tuples
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

        match_result = MatchResult(
            matched_slice=matched_slice,
            matched_class=matched_class,
            child_matches=child_matches,
            segment_kwargs=segment_kwargs,
            insert_segments=insert_segments,
        )

        return match_result, parse_errors

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
        from sqlfluffrs import RsToken

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
    ) -> list:
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
            else:
                # Cannot reconstruct RsToken from Python segment
                raise ValueError(
                    f"Cannot extract RsToken from segment {segment!r}. "
                    f"Unsupported segment type: {type(segment).__name__}."
                )

        return tokens
