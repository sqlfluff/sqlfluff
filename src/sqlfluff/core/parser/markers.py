"""Implements the FilePositionMarker class.

This class is a construct to keep track of positions within a file.
"""

from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

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

    @classmethod
    def from_point(cls, source_point: int, templated_point: int, templated_file: "TemplatedFile"):
        """Convenience method for creating point markers."""
        return cls(
            slice(source_point, source_point),
            slice(templated_point, templated_point),
            templated_file
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
        return cls(
            source_slice,
            templated_slice,
            templated_file
        )
    
    def to_source_string(self):
        line, pos = self.templated_file.get_line_pos_of_char_pos(
            self.source_slice.start, source=True
        )
        return "[C:{0:4d}, L:{1:3d}, P:{2:3d}]".format(
            self.source_slice.start, line, pos
        )

    def start_point_marker(self):
        """Get a point marker from the start."""
        return self.__class__.from_point(
            self.source_slice.start,
            self.templated_slice.start,
            templated_file=self.templated_file,
        )

    def end_point_marker(self):
        """Get a point marker from the start."""
        return self.__class__.from_point(
            self.source_slice.stop,
            self.templated_slice.stop,
            templated_file=self.templated_file,
        )

    def is_point(self):
        """A marker is a point if it has zero length in templated and source file."""
        return (self.source_slice.start == self.source_slice.stop) and (self.templated_slice.start == self.templated_slice.stop)

    def is_literal(self):
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


class FilePositionMarker:
    """This class is a construct to keep track of positions within a file."""

    slots = ["statement_index", "line_no", "line_pos", "char_pos"]

    def __init__(
        self,
        statement_index: Optional[int] = 1,
        line_no: int = 1,
        line_pos: Optional[int] = 1,
        char_pos: int = 0,
    ):
        # NB: statement_index and line_pos are optional so that
        # we can use position markers to flag up errors which
        # are specific to a line but we don't (or can't) know
        # precisely where within that line the issue is.
        self.statement_index = statement_index
        self.line_no = line_no
        self.line_pos = line_pos
        self.char_pos = char_pos

    def __str__(self):
        return "[{0}]({1}, {2}, {3})".format(
            self.char_pos, self.statement_index, self.line_no, self.line_pos
        )

    def __gt__(self, other):
        return self.char_pos > other.char_pos

    def __lt__(self, other):
        return self.char_pos < other.char_pos

    def __ge__(self, other):
        return self.char_pos >= other.char_pos

    def __le__(self, other):
        return self.char_pos <= other.char_pos

    def __eq__(self, other):
        return (
            (self.statement_index == other.statement_index)
            and (self.line_no == other.line_no)
            and (self.line_pos == other.line_pos)
            and (self.char_pos == other.char_pos)
        )

    def advance_by(self, raw="", idx=0):
        """Construct a new `FilePositionMarker` at a point ahead of this one.

        Args:
            raw (:obj:`str`): The string to indicate how we should advance
                the position.
            idx (:obj:`int`, optional): The statement index to advance by.

        """
        stmt = self.statement_index
        line = self.line_no
        pos = self.line_pos
        char_pos = self.char_pos
        for elem in raw:
            char_pos += 1
            if elem == "\n":
                line += 1
                pos = 1
            else:
                pos += 1
        return FilePositionMarker(stmt + idx, line, pos, char_pos)

    def shift_to(self, other):
        """Shift the position of this marker to that of other.

        The result is trivial for unenriched markers.
        """
        return other

    def combine(self, *others):
        """Work out a new position marker from that of the parent segments.

        The result is trivial for unenriched markers.
        """
        if hasattr(others[0], "pos_marker"):
            return others[0].pos_marker
        return others[0]

    def strip(self):
        """Strip back anything enriched from this position marker."""
        return self


class EnrichedFilePositionMarker(FilePositionMarker):
    """A more advanced file position marker which keeps track of source position."""

    slots = ["templated_slice", "source_slice", "is_literal", "source_pos_marker"]

    def __init__(
        self,
        statement_index: int,
        line_no: int,
        line_pos: int,
        char_pos: int,
        templated_slice: slice,
        source_slice: slice,
        is_literal: bool,
        source_pos_marker: FilePositionMarker,
    ):
        super().__init__(statement_index, line_no, line_pos, char_pos)
        self.templated_slice = templated_slice
        self.source_slice = source_slice
        self.is_literal = is_literal
        self.source_pos_marker = source_pos_marker

    def __str__(self):
        return str(self.source_pos_marker)

    @property
    def _source_marker(self):
        return self.source_pos_marker

    def shift_to(self, other):
        """Shift the position of this marker to that of other.

        We keep the same references in the source file, and the templated
        file, but update the references.
        """
        return EnrichedFilePositionMarker(
            statement_index=other.statement_index,
            line_no=other.line_no,
            line_pos=other.line_pos,
            char_pos=other.char_pos,
            templated_slice=self.templated_slice,
            source_slice=self.source_slice,
            is_literal=self.is_literal,
            source_pos_marker=self.source_pos_marker,
        )

    def combine(self, *others):
        """Work out a new position marker from that of the parent segments.

        We *combine* the spans.
        """
        # Make a list out of others, because we're going to use it a couple of times.
        return EnrichedFilePositionMarker(
            statement_index=self.statement_index,
            line_no=self.line_no,
            line_pos=self.line_pos,
            char_pos=self.char_pos,
            templated_slice=slice(
                min(
                    other.templated_slice.start
                    for other in others
                    if hasattr(other, "templated_slice")
                ),
                max(
                    other.templated_slice.stop
                    for other in others
                    if hasattr(other, "templated_slice")
                ),
            ),
            source_slice=slice(
                min(
                    other.source_slice.start
                    for other in others
                    if hasattr(other, "templated_slice")
                ),
                max(
                    other.source_slice.stop
                    for other in others
                    if hasattr(other, "templated_slice")
                ),
            ),
            is_literal=all(getattr(other, "is_literal", True) for other in others),
            source_pos_marker=self.source_pos_marker,
        )

    def strip(self):
        """Strip back anything enriched from this position marker."""
        return FilePositionMarker(
            statement_index=self.statement_index,
            line_no=self.line_no,
            line_pos=self.line_pos,
            char_pos=self.char_pos,
        )
