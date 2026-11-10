"""Tests for the ParseContext class."""

import pytest

from sqlfluff.core.parser import StringParser
from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.segments import KeywordSegment


def test__parser__context_deeper_match_restores_state():
    """Test deeper_match sets and then restores the context state."""
    ctx = ParseContext(dialect=None, max_parse_depth=0)
    outer = StringParser("outer", KeywordSegment)
    inner = StringParser("inner", KeywordSegment)
    with ctx.deeper_match(name="Outer", push_terminators=[outer]):
        assert ctx.match_segment == "Outer"
        assert ctx.match_depth == 1
        assert ctx.terminators == (outer,)
        with ctx.deeper_match(
            name="Inner",
            clear_terminators=True,
            push_terminators=[inner],
            track_progress=False,
        ) as inner_ctx:
            assert inner_ctx is ctx
            assert ctx.match_segment == "Inner"
            assert ctx.match_depth == 2
            assert ctx.terminators == (inner,)
            assert ctx.track_progress is False
        assert ctx.match_segment == "Outer"
        assert ctx.match_depth == 1
        assert ctx.terminators == (outer,)
        assert ctx.track_progress is True
    assert ctx.match_segment == "File"
    assert ctx.match_depth == 0
    assert ctx.terminators == ()


def test__parser__context_deeper_match_restores_state_on_error():
    """Test deeper_match restores the context state if the match raises."""
    ctx = ParseContext(dialect=None, max_parse_depth=0)
    terminator = StringParser("foo", KeywordSegment)
    with pytest.raises(ValueError):
        with ctx.deeper_match(name="Failing", push_terminators=[terminator]):
            raise ValueError("Match failed")
    assert ctx.match_segment == "File"
    assert ctx.match_depth == 0
    assert ctx.terminators == ()
