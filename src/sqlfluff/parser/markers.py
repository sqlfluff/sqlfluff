"""Implements the FilePositionMarker class.

This class is a construct to keep track of positions within a file.
"""

from collections import namedtuple

protoFilePositionMarker = namedtuple('FilePositionMarker', ['statement_index', 'line_no', 'line_pos', 'char_pos'])


class FilePositionMarker(protoFilePositionMarker):
    """This class is a construct to keep track of positions within a file."""

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
            if elem == '\n':
                line += 1
                pos = 1
            else:
                pos += 1
        return FilePositionMarker(stmt + idx, line, pos, char_pos)

    @classmethod
    def from_fresh(cls):
        """Construct a fresh position marker.

        This should be the default way of creating a new postion marker, and
        is where we define what the `start` of a file looks like.
        """
        return cls(1, 1, 1, 0)

    def __str__(self):
        return "[{0}]({1}, {2}, {3})".format(
            self.char_pos, self.statement_index, self.line_no, self.line_pos)

    def __gt__(self, other):
        return self.char_pos > other.char_pos

    def __lt__(self, other):
        return self.char_pos < other.char_pos

    def __eq__(self, other):
        return ((self.statement_index == other.statement_index)
                and (self.line_no == other.line_no)
                and (self.line_pos == other.line_pos)
                and (self.char_pos == other.char_pos))
