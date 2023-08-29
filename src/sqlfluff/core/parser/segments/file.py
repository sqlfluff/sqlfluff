"""Definition of the BaseFileSegment."""

from abc import abstractmethod
from typing import Optional, Set, Tuple

from sqlfluff.core.parser.markers import PositionMarker
from sqlfluff.core.parser.segments.base import BaseSegment


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
