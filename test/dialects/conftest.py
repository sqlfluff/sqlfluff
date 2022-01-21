"""Sharing fixtures to test the dialects."""
import pytest

import logging

from sqlfluff.core import FluffConfig, Linter
from sqlfluff.core.parser import (
    Lexer,
    BaseSegment,
    RawSegment,
    StringParser,
)
from sqlfluff.core.parser.context import RootParseContext
from sqlfluff.core.parser.match_result import MatchResult


def lex(raw, config):
    """Basic parsing for the tests below."""
    # Set up the lexer
    lex = Lexer(config=config)
    # Lex the string for matching. For a good test, this would
    # arguably happen as a fixture, but it's easier to pass strings
    # as parameters than pre-lexed segment strings.
    seg_list, vs = lex.lex(raw)
    assert not vs
    print(seg_list)
    return seg_list


def validate_segment(segmentref, config):
    """Get and validate segment for tests below."""
    Seg = config.get("dialect_obj").ref(segmentref)
    if isinstance(Seg, StringParser):
        return Seg
    try:
        if issubclass(Seg, BaseSegment):
            return Seg
    except TypeError:
        pass
    raise TypeError(
        "{} is not of type Segment or StringParser. Test is invalid.".format(segmentref)
    )


def _dialect_specific_segment_parses(dialect, segmentref, raw, caplog):
    """Test that specific segments parse as expected.

    NB: We're testing the PARSE function not the MATCH function
    although this will be a recursive parse and so the match
    function of SUBSECTIONS will be tested if present. The match
    function of the parent will not be tested.
    """
    config = FluffConfig(overrides=dict(dialect=dialect))
    seg_list = lex(raw, config=config)
    Seg = validate_segment(segmentref, config=config)

    # This test is different if we're working with RawSegment
    # derivatives or not.
    if isinstance(Seg, StringParser) or issubclass(Seg, RawSegment):
        print("Raw/Parser route...")
        with RootParseContext.from_config(config) as ctx:
            with caplog.at_level(logging.DEBUG):
                parsed = Seg.match(segments=seg_list, parse_context=ctx)
        assert isinstance(parsed, MatchResult)
        assert len(parsed.matched_segments) == 1
        print(parsed)
        parsed = parsed.matched_segments[0]
        print(parsed)
    else:
        print("Base route...")
        # Construct an unparsed segment
        seg = Seg(seg_list, pos_marker=seg_list[0].pos_marker)
        # Perform the match (THIS IS THE MEAT OF THE TEST)
        with RootParseContext.from_config(config) as ctx:
            with caplog.at_level(logging.DEBUG):
                parsed = seg.parse(parse_context=ctx)
        print(parsed)
        assert isinstance(parsed, Seg)

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
    seg_list = lex(raw, config=config)
    Seg = validate_segment(segmentref, config=config)

    with RootParseContext.from_config(config) as ctx:
        with caplog.at_level(logging.DEBUG):
            match = Seg.match(segments=seg_list, parse_context=ctx)

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
