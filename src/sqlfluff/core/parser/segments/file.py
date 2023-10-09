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

        # Set up the progress bar for parsing.
        _final_seg = segments[-1]
        assert _final_seg.pos_marker
        _closing_position = _final_seg.pos_marker.templated_slice.stop
        with parse_context.progress_bar(_closing_position):
            # NOTE: Don't call .match() on the segment class itself, but go
            # straight to the match grammar inside.
            match = cls.match_grammar.match(
                segments[:_end_idx], _start_idx, parse_context
            )

        parse_context.logger.info("Root Match:\n%s", match.stringify())
        _matched = match.apply(segments)
        _unmatched = segments[match.matched_slice.stop : _end_idx]

        content: Tuple[BaseSegment, ...]
        if not match:
            content = (
                UnparsableSegment(
                    segments[_start_idx:_end_idx], expected=str(cls.match_grammar)
                ),
            )
        elif _unmatched:
            _idx = 0
            for _idx in range(len(_unmatched)):
                if _unmatched[_idx].is_code:
                    break
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

        return cls(
            segments[:_start_idx] + content + segments[_end_idx:],
            fname=fname,
        )
