""" The Test file for Chunks """

import pytest

from sqlfluff.chunks import PositionedChunk


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
