"""Implements the PositionMarker class.

This class is a construct to keep track of positions within a file.
"""

from dataclasses import dataclass
from typing import Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from sqlfluff.core.templaters import TemplatedFile


@dataclass(frozen=True)
class PositionMarker:
    """A reference to a position in a file.

    Things to note:
        - This combines the previous functionality of FilePositionMarker
          and EnrichedFilePositionMarker. Additionally it contains a reference
          to the original templated file.
        - It no longer explicitly stores a line number or line position.
          This is extrapolated from the templated file as required.
        - It makes no effort to store position in the file after any fixes
          have been applied. Position markers for inserted elements will
          have a zero width in both the source and templated slice.
        - The use of a `statement_index` is deprecated as it was never used.
    """

    source_slice: slice
    templated_slice: slice
    templated_file: "TemplatedFile"

    def __str__(self):
        return self.to_source_string()

    def __gt__(self, other):
        # Only allow comparison of point markers.
        if not self.is_point() or not other.is_point():
            raise ValueError("Can only compare point markers.")
        return self.source_slice.start > other.source_slice.start

    def __lt__(self, other):
        # Only allow comparison of point markers.
        if not self.is_point() or not other.is_point():
            raise ValueError("Can only compare point markers.")
        return self.source_slice.start < other.source_slice.start

    def __ge__(self, other):
        return (self > other) or (self == other)

    def __le__(self, other):
        return (self < other) or (self == other)

    @classmethod
    def from_point(
        cls, source_point: int, templated_point: int, templated_file: "TemplatedFile"
    ):
        """Convenience method for creating point markers."""
        return cls(
            slice(source_point, source_point),
            slice(templated_point, templated_point),
            templated_file,
        )

    @classmethod
    def from_child_markers(cls, *markers):
        """Create a parent marker from it's children."""
        source_slice = slice(
            min(m.source_slice.start for m in markers),
            max(m.source_slice.stop for m in markers),
        )
        templated_slice = slice(
            min(m.templated_slice.start for m in markers),
            max(m.templated_slice.stop for m in markers),
        )
        templated_files = set(m.templated_file for m in markers)
        if len(templated_files) != 1:
            raise ValueError("Attempted to make a parent marker from multiple files.")
        templated_file = templated_files.pop()
        return cls(source_slice, templated_slice, templated_file)

    def source_position(self) -> Tuple[int, int]:
        """Return the line and position of this marker in the source."""
        return self.templated_file.get_line_pos_of_char_pos(
            self.source_slice.start, source=True
        )

    def templated_position(self) -> Tuple[int, int]:
        """Return the line and position of this marker in the source."""
        return self.templated_file.get_line_pos_of_char_pos(
            self.templated_slice.start, source=False
        )

    @property
    def line_no(self) -> int:
        return self.source_position()[0]

    @property
    def line_pos(self) -> int:
        return self.source_position()[1]

    def to_source_string(self) -> str:
        line, pos = self.source_position()
        return "[C:{0:4d}, L:{1:3d}, P:{2:3d}]".format(
            self.source_slice.start, line, pos
        )

    def start_point_marker(self) -> "PositionMarker":
        """Get a point marker from the start."""
        return self.__class__.from_point(
            self.source_slice.start,
            self.templated_slice.start,
            templated_file=self.templated_file,
        )

    def end_point_marker(self) -> "PositionMarker":
        """Get a point marker from the start."""
        return self.__class__.from_point(
            self.source_slice.stop,
            self.templated_slice.stop,
            templated_file=self.templated_file,
        )

    @staticmethod
    def slice_is_point(test_slice):
        """Is this slice a point."""
        return test_slice.start == test_slice.stop

    def is_point(self) -> bool:
        """A marker is a point if it has zero length in templated and source file."""
        return self.slice_is_point(self.source_slice) and self.slice_is_point(
            self.templated_slice
        )

    def is_literal(self) -> bool:
        """Infer literalness from context."""
        # NOTE: We should define what the implication of is_literal is here.
        # TODO: I think we were inconsistent in whether a zero length source slice
        # is (or is not) literal. The lexer initially defined it as False, this
        # function will say True. Not sure what the implications of that are yet.
        # NOTE: So far I can see it only controls:
        # 1. The patch_type of a FixPatch, which appears to then never be referred to.
        # 2. The ignoring of templated sections in `remove_templated_errors`.
        # 3. Whether we can return simply in `iter_patches`.
        # 4. The application of L046 which is looking for tags.
        return self.templated_file.is_source_slice_literal(self.source_slice)
