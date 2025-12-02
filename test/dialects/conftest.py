"""Sharing fixtures to test the dialects."""

import logging

import pytest

from sqlfluff.core import FluffConfig, Linter
from sqlfluff.core.parser import BaseSegment, Lexer
from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.match_result import MatchResult
from sqlfluff.core.parser.matchable import Matchable


def lex(raw, config):
    """Basic parsing for the tests below."""
    # Set up the lexer
    lex = Lexer(config=config)
    # Lex the string for matching. For a good test, this would
    # arguably happen as a fixture, but it's easier to pass strings
    # as parameters than pre-lexed segment strings.
    segments, vs = lex.lex(raw)
    assert not vs
    print(segments)
    return segments


def validate_segment(segmentref, config):
    """Get and validate segment for tests below."""
    Seg = config.get("dialect_obj").ref(segmentref)
    if isinstance(Seg, Matchable):
        return Seg
    try:
        if issubclass(Seg, BaseSegment):
            return Seg
    except TypeError:
        pass
    raise TypeError(
        "{} is not of type Segment or Matchable. Test is invalid.".format(segmentref)
    )


def _dialect_specific_segment_parses(dialect, segmentref, raw, caplog):
    """Test that specific segments parse as expected.

    NB: We're testing the PARSE function not the MATCH function
    although this will be a recursive parse and so the match
    function of SUBSECTIONS will be tested if present. The match
    function of the parent will not be tested.
    """
    config = FluffConfig(overrides=dict(dialect=dialect))
    segments = lex(raw, config=config)
    Seg = validate_segment(segmentref, config=config)

    # Most segments won't handle the end of file marker. We should strip it.
    if segments[-1].is_type("end_of_file"):
        segments = segments[:-1]

    ctx = ParseContext.from_config(config)
    with caplog.at_level(logging.DEBUG):
        result = Seg.match(segments, 0, parse_context=ctx)
    assert isinstance(result, MatchResult)
    parsed = result.apply(segments)
    assert len(parsed) == 1
    print(parsed)
    parsed = parsed[0]

    # Check we get a good response
    print(parsed)
    print(type(parsed))
    print(type(parsed.raw))
    # Check we're all there.
    assert parsed.raw == raw
    # Check that there's nothing un parsable
    typs = parsed.type_set()
    assert "unparsable" not in typs


def _dialect_specific_segment_not_match(dialect, segmentref, raw, caplog):
    """Test that specific segments do not match.

    NB: We're testing the MATCH function not the PARSE function.
    This is the opposite to the above.
    """
    config = FluffConfig(overrides=dict(dialect=dialect))
    segments = lex(raw, config=config)
    Seg = validate_segment(segmentref, config=config)

    ctx = ParseContext.from_config(config)
    with caplog.at_level(logging.DEBUG):
        match = Seg.match(segments, 0, parse_context=ctx)

    assert not match


def _validate_dialect_specific_statements(dialect, segment_cls, raw, stmt_count):
    """This validates one or multiple statements against specified segment class.

    It even validates the number of parsed statements with the number of expected
    statements.
    """
    lnt = Linter(dialect=dialect)
    parsed = lnt.parse_string(raw)
    assert len(parsed.violations) == 0

    # Find any unparsable statements
    typs = parsed.tree.type_set()
    assert "unparsable" not in typs

    # Find the expected type in the parsed segment
    child_segments = [seg for seg in parsed.tree.recursive_crawl(segment_cls.type)]
    assert len(child_segments) == stmt_count

    # Check if all child segments are the correct type
    for c in child_segments:
        assert isinstance(c, segment_cls)


@pytest.fixture()
def dialect_specific_segment_parses():
    """Fixture to check specific segments of a dialect."""
    return _dialect_specific_segment_parses


@pytest.fixture()
def dialect_specific_segment_not_match():
    """Check specific segments of a dialect which will not match to a segment."""
    return _dialect_specific_segment_not_match


@pytest.fixture()
def validate_dialect_specific_statements():
    """This validates one or multiple statements against specified segment class.

    It even validates the number of parsed statements with the number of expected
    statements.
    """
    return _validate_dialect_specific_statements
