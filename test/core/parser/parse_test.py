"""The Test file for The New Parser (Grammar Classes)."""

from sqlfluff.core.errors import SQLParseError
from sqlfluff.core.linter.linter import Linter
from sqlfluff.core.parser import Anything, BaseSegment, KeywordSegment, StringParser
from sqlfluff.core.parser.context import ParseContext

BarKeyword = StringParser("bar", KeywordSegment)


class BasicSegment(BaseSegment):
    """A basic segment for testing parse and expand."""

    type = "basic"
    match_grammar = Anything()


def test__parser__parse_match(test_segments):
    """Test match method on a real segment."""
    ctx = ParseContext(dialect=None)
    # This should match and have consumed everything, which should
    # now be part of a BasicSegment.
    m = BasicSegment.match(test_segments[:1], parse_context=ctx)
    assert m
    assert len(m.matched_segments) == 1
    assert isinstance(m.matched_segments[0], BasicSegment)
    assert m.matched_segments[0].segments[0].type == "raw"


def test__parser__parse_error():
    """Test that SQLParseError is raised for unparsable section."""
    in_str = "SELECT ;"
    lnt = Linter(dialect="ansi")
    parsed = lnt.parse_string(in_str)

    assert len(parsed.violations) == 1
    violation = parsed.violations[0]
    assert isinstance(violation, SQLParseError)
    assert violation.desc() == "Line 1, Position 1: Found unparsable section: 'SELECT'"

    # Check that the expected labels work for logging.
    # TODO: This is more specific that in previous iterations, but we could
    # definitely make this easier to read.
    assert (
        'Expected: "<Delimited: '
        "[<Ref: 'SelectClauseElementSegment'>]> "
        "after <KeywordSegment: ([L:  1, P:  1]) 'SELECT'>. "
        "Found nothing."
    ) in parsed.tree.stringify()
