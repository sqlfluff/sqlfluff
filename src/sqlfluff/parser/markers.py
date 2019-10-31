
from collections import namedtuple

protoFilePositionMarker = namedtuple('FilePositionMarker', ['statement_index', 'line_no', 'line_pos', 'char_pos'])


class FilePositionMarker(protoFilePositionMarker):
    def advance_by(self, raw="", idx=0):
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
        # Defines what a fresh one of these looks like
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
