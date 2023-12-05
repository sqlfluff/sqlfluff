"""Implements the PositionMarker class.

This class is a construct to keep track of positions within a file.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple

from sqlfluff.core.helpers.slice import zero_slice

if TYPE_CHECKING:
    from sqlfluff.core.templaters import TemplatedFile  # pragma: no cover


@dataclass(frozen=True)
class PositionMarker:
    """A reference to a position in a file.

    Things to note:
        - This combines the previous functionality of FilePositionMarker
          and EnrichedFilePositionMarker. Additionally it contains a reference
          to the original templated file.
        - It no longer explicitly stores a line number or line position in the
          source or template. This is extrapolated from the templated file as required.
        - Positions in the source and template are with slices and therefore identify
          ranges.
        - Positions within the fixed file are identified with a line number and line
          position, which identify a point.
        - Arithmetic comparisons are on the location in the fixed file.
    """

    source_slice: slice
    templated_slice: slice
    templated_file: "TemplatedFile"
    # If not set, these will be initialised in the post init.
    working_line_no: int = -1
    working_line_pos: int = -1

    def __post_init__(self) -> None:
        # If the working position has not been explicitly set
        # then infer it from the position in the templated file.
        # This is accurate up until the point that any fixes have
        # been applied.
        if self.working_line_no == -1 or self.working_line_pos == -1:
            line_no, line_pos = self.templated_position()
            # Use the base method because we're working with a frozen class
            object.__setattr__(self, "working_line_no", line_no)
            object.__setattr__(self, "working_line_pos", line_pos)

    def __str__(self) -> str:
        return self.to_source_string()

    def __gt__(self, other: "PositionMarker") -> bool:
        return self.working_loc > other.working_loc

    def __lt__(self, other: "PositionMarker") -> bool:
        return self.working_loc < other.working_loc

    def __ge__(self, other: "PositionMarker") -> bool:
        return self.working_loc >= other.working_loc

    def __le__(self, other: "PositionMarker") -> bool:
        return self.working_loc <= other.working_loc

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, PositionMarker):
            return False  # pragma: no cover
        return self.working_loc == other.working_loc

    @property
    def working_loc(self) -> Tuple[int, int]:
        """Location tuple for the working position."""
        return self.working_line_no, self.working_line_pos

    def working_loc_after(self, raw: str) -> Tuple[int, int]:
        """Location tuple for the working position."""
        return self.infer_next_position(
            raw,
            self.working_line_no,
            self.working_line_pos,
        )

    @classmethod
    def from_point(
        cls,
        source_point: int,
        templated_point: int,
        templated_file: "TemplatedFile",
        **kwargs: int,  # kwargs can only contain working_line positions
    ) -> "PositionMarker":
        """Convenience method for creating point markers."""
        return cls(
            zero_slice(source_point),
            zero_slice(templated_point),
            templated_file,
            **kwargs,
        )

    @classmethod
    def from_points(
        cls,
        start_point_marker: "PositionMarker",
        end_point_marker: "PositionMarker",
    ) -> "PositionMarker":
        """Construct a position marker from the section between two points."""
        return cls(
            slice(
                start_point_marker.source_slice.start,
                end_point_marker.source_slice.stop,
            ),
            slice(
                start_point_marker.templated_slice.start,
                end_point_marker.templated_slice.stop,
            ),
            # The templated file references from the point markers
            # should be the same, so we're just going to pick one.
            # TODO: If we assert that in this function, it's actually not
            # true - but preliminary debugging on this did not reveal why.
            start_point_marker.templated_file,
            # Line position should be of the _start_ of the section.
            start_point_marker.working_line_no,
            start_point_marker.working_line_pos,
        )

    @classmethod
    def from_child_markers(
        cls, *markers: Optional["PositionMarker"]
    ) -> "PositionMarker":
        """Create a parent marker from it's children."""
        source_slice = slice(
            min(m.source_slice.start for m in markers if m),
            max(m.source_slice.stop for m in markers if m),
        )
        templated_slice = slice(
            min(m.templated_slice.start for m in markers if m),
            max(m.templated_slice.stop for m in markers if m),
        )
        templated_files = {m.templated_file for m in markers if m}
        if len(templated_files) != 1:  # pragma: no cover
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
        """Return the line number in the source."""
        return self.source_position()[0]

    @property
    def line_pos(self) -> int:
        """Return the line position in the source."""
        return self.source_position()[1]

    def to_source_string(self) -> str:
        """Make a formatted string of this position."""
        line, pos = self.source_position()
        return f"[L:{line:3d}, P:{pos:3d}]"

    def start_point_marker(self) -> "PositionMarker":
        """Get a point marker from the start."""
        return self.__class__.from_point(
            self.source_slice.start,
            self.templated_slice.start,
            templated_file=self.templated_file,
            # Start points also pass on the working position.
            working_line_no=self.working_line_no,
            working_line_pos=self.working_line_pos,
        )

    def end_point_marker(self) -> "PositionMarker":
        """Get a point marker from the end."""
        return self.__class__.from_point(
            self.source_slice.stop,
            self.templated_slice.stop,
            templated_file=self.templated_file,
        )

    @staticmethod
    def slice_is_point(test_slice: slice) -> bool:
        """Is this slice a point."""
        is_point: bool = test_slice.start == test_slice.stop
        return is_point

    def is_point(self) -> bool:
        """A marker is a point if it has zero length in templated and source file."""
        return self.slice_is_point(self.source_slice) and self.slice_is_point(
            self.templated_slice
        )

    @staticmethod
    def infer_next_position(raw: str, line_no: int, line_pos: int) -> Tuple[int, int]:
        """Using the raw string provided to infer the position of the next.

        NB: Line position in 1-indexed.
        """
        # No content?
        if not raw:
            return line_no, line_pos
        split = raw.split("\n")
        return (
            line_no + len(split) - 1,
            line_pos + len(raw) if len(split) == 1 else len(split[-1]) + 1,
        )

    def with_working_position(self, line_no: int, line_pos: int) -> "PositionMarker":
        """Copy this position and replace the working position."""
        return self.__class__(
            source_slice=self.source_slice,
            templated_slice=self.templated_slice,
            templated_file=self.templated_file,
            working_line_no=line_no,
            working_line_pos=line_pos,
        )

    def is_literal(self) -> bool:
        """Infer literalness from context.

        is_literal should return True if a fix can be applied across this area
        in the templated file while being confident that the fix is still
        appropriate in the source file. This obviously applies to any slices
        which are the same in the source and the templated files. Slices which
        are zero-length in the source are also "literal" because they can't be
        "broken" by any fixes, because they don't exist in the source. This
        includes meta segments and any segments added during the fixing process.

        This value is used for:
        - Ignoring linting errors in templated sections.
        - Whether `_iter_templated_patches` can return without recursing.
        - Whether certain rules (such as JJ01) are triggered.
        """
        return self.templated_file.is_source_slice_literal(self.source_slice)

    def source_str(self) -> str:
        """Returns the string in the source at this position."""
        return self.templated_file.source_str[self.source_slice]

    def to_source_dict(self) -> Dict[str, int]:
        """Serialise the source position."""
        return self.templated_file.source_position_dict_from_slice(self.source_slice)
