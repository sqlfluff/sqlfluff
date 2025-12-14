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

if TYPE_CHECKING:  # pragma: no cover
    from sqlfluff.core.config import FluffConfig
    from sqlfluff.core.parser.segments import BaseSegment
    from sqlfluff.core.templaters.base import TemplatedFile
    from sqlfluffrs import RsMatchResult


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

        # Create the Rust parser
        self._rs_parser = RsParser(dialect=self.config.get("dialect"))

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
            # Log the error and return None (like Python parser does)
            print(f"Rust parser error: {e}")
            return None

        # Convert RsMatchResult to Python MatchResult
        py_match_result = self._convert_rs_match_result(rs_match_result)

        # Apply the match result to construct the BaseSegment tree
        # PYTHON PARITY: Pass only the code portion (segments[_start_idx:_end_idx])
        # because match result indices are relative to this trimmed array
        result_segments = py_match_result.apply(segments[_start_idx:_end_idx])

        # PYTHON PARITY: Add back any unmatched segments after the match
        # (relative to the _start_idx:_end_idx range)
        _unmatched = segments[
            _start_idx + py_match_result.matched_slice.stop : _end_idx
        ]

        # Wrap in FileSegment following root_parse pattern
        dialect = self.config.get("dialect_obj")
        file_segment_cls = dialect.get_segment("FileSegment")

        # PYTHON PARITY: Reassemble with leading non-code + matched + unmatched + trailing non-code
        content = result_segments + _unmatched
        final_segments = segments[:_start_idx] + content + segments[_end_idx:]

        result = file_segment_cls(segments=final_segments, fname=fname)

        if parse_statistics:
            print("Warning: parse_statistics not yet implemented for Rust parser")

        return result

    def _convert_rs_match_result(
        self, rs_match: "RsMatchResult", depth: int = 0
    ) -> MatchResult:
        """Convert Rust MatchResult to Python MatchResult.

        Args:
            rs_match: RsMatchResult from Rust parser
            depth: Current recursion depth for debugging

        Returns:
            Python MatchResult with equivalent structure
        """
        # Get the matched slice
        start, stop = rs_match.matched_slice
        matched_slice = slice(start, stop)

        # Convert child matches recursively
        child_matches = tuple(
            self._convert_rs_match_result(child, depth + 1)
            for child in rs_match.child_matches
        )

        # Determine matched_class
        # The Rust parser now includes actual Python class names (from codegen)
        # in matched_class, so we can use them directly without conversion.
        matched_class = None
        if rs_match.matched_class:
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

        # Extract insert_segments (Indent/Dedent meta segments)
        insert_segments = ()
        if rs_match.insert_segments:
            from sqlfluff.core.parser.segments.meta import Indent, Dedent

            meta_segment_map = {
                "indent": Indent,
                "dedent": Dedent,
            }
            insert_segments = tuple(
                (idx, meta_segment_map[seg_type])
                for idx, seg_type in rs_match.insert_segments
            )

        return MatchResult(
            matched_slice=matched_slice,
            matched_class=matched_class,
            child_matches=child_matches,
            segment_kwargs=segment_kwargs,
            insert_segments=insert_segments,
        )

    def _extract_tokens_from_segments(
        self, segments: tuple["BaseSegment", ...]
    ) -> list:
        """Extract RsToken objects from RawSegments.

        This is a temporary solution. In the optimized flow, we would pass
        RsToken objects directly from lexer to parser without converting to
        RawSegment first.

        Args:
            segments: Tuple of RawSegment objects

        Returns:
            List of RsToken objects (or compatible token objects)
        """
        tokens = []
        for segment in segments:
            # Check if segment has _rstoken attribute (cached original token)
            if hasattr(segment, "_rstoken"):
                tokens.append(segment._rstoken)
            else:
                # Cannot reconstruct RsToken from Python segment - this happens with
                # templated segments or segments created by Python code
                raise ValueError(
                    f"Cannot extract RsToken from segment {segment!r}. "
                    f"Rust parser requires segments with _rstoken attribute. "
                    f"This may indicate templated content which is not yet supported."
                )

        return tokens
