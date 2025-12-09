"""Python wrapper for Rust parser that returns BaseSegment trees.

This module provides RustParser, a drop-in replacement for the Python Parser
that uses the Rust implementation under the hood but returns Python BaseSegment
objects for compatibility with the linter infrastructure.
"""

from typing import TYPE_CHECKING, Optional

from sqlfluff.core.parser.rsparser_adapter import rsnode_to_segment

if TYPE_CHECKING:  # pragma: no cover
    from sqlfluff.core.config import FluffConfig
    from sqlfluff.core.parser.segments import BaseSegment
    from sqlfluff.core.templaters.base import TemplatedFile


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
        if not segments:
            return None

        # Extract templated_file from first segment if not provided
        if tf is None and segments:
            first_seg = segments[0]
            if hasattr(first_seg, "pos_marker") and first_seg.pos_marker:
                tf = first_seg.pos_marker.templated_file

        # Extract the original RsToken objects from the RawSegments
        # For now, we need to reconstruct them - in the future we could cache them
        tokens = self._extract_tokens_from_segments(segments)

        # Parse using Rust parser
        try:
            rsnode = self._rs_parser.parse_from_tokens(tokens)
        except Exception as e:
            # Log the error and return None (like Python parser does)
            # TODO: Better error handling
            print(f"Rust parser error: {e}")
            return None

        # Convert RsNode to BaseSegment
        result = rsnode_to_segment(rsnode, tokens, self.config, tf)

        # Handle _SegmentTuple (multiple top-level segments)
        # This shouldn't happen for a valid parse, but handle it gracefully
        if (
            result
            and hasattr(result, "segments")
            and hasattr(result, "__class__")
            and result.__class__.__name__ == "_SegmentTuple"
        ):
            # Wrap in FileSegment if we have multiple top-level segments
            from sqlfluff.core.parser.markers import PositionMarker

            # Get FileSegment from the dialect
            dialect = self.config.get("dialect_obj")
            file_segment_cls = dialect.get_segment("FileSegment")

            segments_list = list(result.segments)
            pos_marker = None
            if segments_list and all(
                hasattr(seg, "pos_marker") and seg.pos_marker for seg in segments_list
            ):
                pos_marker = PositionMarker.from_child_markers(
                    [seg.pos_marker for seg in segments_list]
                )
            result = file_segment_cls(
                segments=tuple(segments_list), pos_marker=pos_marker
            )

        # TODO: Handle parse_statistics when requested
        if parse_statistics:
            print("Warning: parse_statistics not yet implemented for Rust parser")

        return result

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
