"""Implements the FilePositionMarker class.

This class is a construct to keep track of positions within a file.
"""


class FilePositionMarker:
    """This class is a construct to keep track of positions within a file."""

    slots = ["statement_index", "line_no", "line_pos", "char_pos"]

    def __init__(
        self, statement_index: int, line_no: int, line_pos: int, char_pos: int
    ):
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

    def __eq__(self, other):
        return (
            (self.statement_index == other.statement_index)
            and (self.line_no == other.line_no)
            and (self.line_pos == other.line_pos)
            and (self.char_pos == other.char_pos)
        )

    @classmethod
    def from_fresh(cls):
        """Construct a fresh position marker.

        This should be the default way of creating a new postion marker, and
        is where we define what the `start` of a file looks like.
        """
        return cls(1, 1, 1, 0)

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
