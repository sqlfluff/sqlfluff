""" The Test file for Chunks """

import pytest

from sqlfluff.chunks import PositionedChunk, ChunkString


# ############## Chunks
def test__chunk__split():
    c = PositionedChunk('foobarbar', 10, 20, None)
    a, b = c.split_at(3)
    assert a == PositionedChunk('foo', 10, 20, None)
    assert b == PositionedChunk('barbar', 13, 20, None)


def test__chunk__split_context_error():
    c = PositionedChunk('foobarbar', 10, 20, 'context')
    with pytest.raises(RuntimeError):
        c.split_at(4)


def test__chunk__subchunk():
    c = PositionedChunk('foobarbar', 10, 20, None)
    r = c.subchunk(3, 6)
    assert r == PositionedChunk('bar', 13, 20, None)


# ############## Chunklist

def test__chunklist__content():
    # Raise an exception if we try to create with anything but chunks
    with pytest.raises(AssertionError):
        ChunkString(1, 2, 3)


def test__chunklist__simple_content():
    # Raise an exception if we try to create with anything but chunks
    cs = ChunkString(PositionedChunk('foobarbar', 1, 20, 'a'), PositionedChunk('foobarbar', 1, 21, 'b'))
    assert list(cs.simple_list()) == [('foobarbar', 'a'), ('foobarbar', 'b')]
