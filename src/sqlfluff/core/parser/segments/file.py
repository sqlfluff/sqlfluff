"""Definition of the BaseFileSegment."""

from abc import abstractmethod
from typing import Optional, Set, Tuple

from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.markers import PositionMarker
from sqlfluff.core.parser.segments.base import BaseSegment, UnparsableSegment


class BaseFileSegment(BaseSegment):
    """A segment representing a whole file or script.

    This is also the default "root" segment of the dialect,
    and so is usually instantiated directly. It therefore
    has no match_grammar.
    """

    type = "file"
    # The file segment is the only one which can start or end with non-code
    can_start_end_non_code = True
    # A file can be empty!
    allow_empty = True

    def __init__(
        self,
        segments: Tuple[BaseSegment, ...],
        pos_marker: Optional[PositionMarker] = None,
        fname: Optional[str] = None,
    ):
        self._file_path = fname
        super().__init__(segments, pos_marker=pos_marker)

    @property
    def file_path(self) -> Optional[str]:
        """File path of a parsed SQL file."""
        return self._file_path

    @abstractmethod
    def get_table_references(self) -> Set[str]:
        """Use parsed tree to extract table references."""

    @classmethod
    def root_parse(
        cls,
        segments: Tuple[BaseSegment, ...],
        parse_context: ParseContext,
        fname: Optional[str] = None,
    ) -> "BaseFileSegment":
        """This is the entry method into parsing a file lexed segments.

        For single pass matching, this trims any non code off
        the start, matches the middle and then trims the end.

        Anything unexpected at the end is regarded as unparsable.
        """
        # Trim the start
        _start_idx = 0
        for _start_idx in range(len(segments)):
            if segments[_start_idx].is_code:
                break

        # Trim the end
        _end_idx = len(segments)
        for _end_idx in range(len(segments), _start_idx - 1, -1):
            if segments[_end_idx - 1].is_code:
                break

        if _start_idx == _end_idx:
            # Return just a file of non-code segments.
            return cls(segments, fname=fname)

        # Match the middle
        assert not hasattr(
            cls, "parse_grammar"
        ), "`parse_grammar` is deprecated on FileSegment."
        assert cls.match_grammar
        # NOTE: Don't call .match() on the segment class itself, but go
        # straight to the match grammar inside.
        match = cls.match_grammar.match(segments[_start_idx:_end_idx], parse_context)
        unmatched = match.unmatched_segments

        if not match:
            raise NotImplementedError(
                f"No match for {fname}: {match} "
                f"{segments[_start_idx:_end_idx]}, "
                f"{_start_idx}:{_end_idx}"
            )
        elif unmatched:
            _idx = 0
            for _idx in range(len(unmatched)):
                if unmatched[_idx].is_code:
                    break
            unmatched = unmatched[:_idx] + (
                UnparsableSegment(
                    unmatched[_idx:], expected="Nothing else in FileSegment."
                ),
            )

        assert match.matched_segments
        return cls(
            segments[:_start_idx]
            + match.matched_segments
            + unmatched
            + segments[_end_idx:],
            fname=fname,
        )
