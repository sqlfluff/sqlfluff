"""The Test file for The New Parser (Grammar Classes)."""

import logging
from sqlfluff.core.errors import SQLParseError
from sqlfluff.core.linter.linter import Linter

from sqlfluff.core.parser import BaseSegment, KeywordSegment, Anything, StringParser
from sqlfluff.core.parser.context import RootParseContext

BarKeyword = StringParser("bar", KeywordSegment)


class BasicSegment(BaseSegment):
    """A basic segment for testing parse and expand."""

    type = "basic"
    match_grammar = Anything()
    parse_grammar = BarKeyword


def test__parser__parse_match(seg_list):
    """Test match method on a real segment."""
    with RootParseContext(dialect=None) as ctx:
        # This should match and have consumed everything, which should
        # now be part of a BasicSegment.
        m = BasicSegment.match(seg_list[:1], parse_context=ctx)
        assert m
        assert len(m.matched_segments) == 1
        assert isinstance(m.matched_segments[0], BasicSegment)
        assert m.matched_segments[0].segments[0].type == "raw"


def test__parser__parse_parse(seg_list, caplog):
    """Test parse method on a real segment."""
    with RootParseContext(dialect=None) as ctx:
        # Match the segment, and get the inner segment
        seg = BasicSegment.match(seg_list[:1], parse_context=ctx).matched_segments[0]
        # Remind ourselves that this should be an unparsed BasicSegment
        assert isinstance(seg, BasicSegment)

        # Now parse that segment, with debugging because this is
        # where we'll need to debug if things fail.
        with caplog.at_level(logging.DEBUG):
            res = seg.parse(parse_context=ctx)
        # Check it's still a BasicSegment
        assert isinstance(res, BasicSegment)
        # Check that we now have a keyword inside
        assert isinstance(res.segments[0], KeywordSegment)


def test__parser__parse_expand(seg_list):
    """Test expand method on a real segment."""
    with RootParseContext(dialect=None) as ctx:
        # Match the segment, and get the matched segments
        segments = BasicSegment.match(seg_list[:1], parse_context=ctx).matched_segments
        # Remind ourselves that this should be tuple containing a BasicSegment
        assert isinstance(segments[0], BasicSegment)

        # Now expand those segments, using the base class version (not that it should matter)
        res = BasicSegment.expand(segments, parse_context=ctx)
        # Check we get an iterable containing a BasicSegment
        assert isinstance(res[0], BasicSegment)
        # Check that we now have a keyword inside
        assert isinstance(res[0].segments[0], KeywordSegment)


def test__parser__parse_error():
    """Test that SQLParseError is raised for unparsable section."""
    in_str = "SELECT ;"
    lnt = Linter()
    parsed = lnt.parse_string(in_str)

    assert len(parsed.violations) == 1
    violation = parsed.violations[0]
    assert isinstance(violation, SQLParseError)
    assert violation.desc() == "Line 1, Position 1: Found unparsable section: 'SELECT'"
