""" Common classes for matching and chunking """

from collections import namedtuple


# chunks should be immutable, they are a subclass of namedtuple (context defaults to None)
class PositionedChunk(namedtuple('ProtoChunk', ['chunk', 'start_pos', 'line_no', 'context'])):
    __slots__ = ()

    def __len__(self):
        return len(self.chunk)

    def contextualise(self, context):
        # Return a copy, just with the context set
        return PositionedChunk(self.chunk, self.start_pos, self.line_no, context=context)

    def split_at(self, pos):
        if self.context:
            raise RuntimeError("Attempting to split a chunk which already has context!")
        if pos <= 0 or pos > len(self):
            raise RuntimeError("Trying to split at wrong index: {pos}".format(pos=pos))
        return (
            PositionedChunk(self.chunk[:pos], self.start_pos, self.line_no, None),
            PositionedChunk(self.chunk[pos:], self.start_pos + pos, self.line_no, None))

    def subchunk(self, start, end=None, context=None):
        if end:
            return PositionedChunk(
                self.chunk[start: end], self.start_pos + start,
                self.line_no, context=context or self.context)
        else:
            return PositionedChunk(
                self.chunk[start:], self.start_pos + start,
                self.line_no, context=context or self.context)


class ChunkString(object):
    def __init__(self, *args):
        assert all([isinstance(elem, PositionedChunk) for elem in args])
        self.chunk_list = list(args)

    def __add__(self, other):
        return ChunkString(*(self.chunk_list + other.chunk_list))

    def __getitem__(self, key):
        return self.chunk_list[key]

    def __len__(self):
        return len(self.chunk_list)

    def context_list(self):
        return [elem.context for elem in self.chunk_list]

    def string_list(self):
        return [elem.chunk for elem in self.chunk_list]

    def simple_list(self):
        # a zipped version of the sring and context
        return zip(self.string_list(), self.context_list())
