"""Tests specific to the ansi dialect."""

import pytest
import logging

from sqlfluff.config import FluffConfig
from sqlfluff.parser import Lexer, FileSegment, ParseContext, BaseSegment, RawSegment
from sqlfluff.parser.match import MatchResult


@pytest.mark.parametrize(
    "raw,res",
    [
        ("a b", ['a', ' ', 'b']),
        ("b.c", ['b', '.', 'c']),
        ("abc \n \t def  ;blah", ['abc', ' ', '\n', ' \t ', 'def', '  ', ';', 'blah'])
    ]
)
def test__dialect__ansi__file_from_raw(raw, res, caplog):
    """Test we don't drop bits on simple examples."""
    config = FluffConfig(overrides=dict(dialect='ansi'))
    with caplog.at_level(logging.DEBUG):
        fs, _ = FileSegment.from_raw(raw, config=config)
    # From just the initial parse, check we're all there
    assert fs.raw == raw
    assert fs.raw_list() == res


# Develop test to check specific elements against specific grammars.
@pytest.mark.parametrize(
    "segmentref,raw",
    [
        ("SelectKeywordSegment", "select"),
        ("NakedIdentifierSegment", "online_sales"),
        ("NumericLiteralSegment", "1000.0"),
        ("ExpressionSegment", "online_sales / 1000.0"),
        ("IntervalExpressionSegment", "INTERVAL 1 YEAR"),
        ("ExpressionSegment",
         "CASE WHEN id = 1 THEN 'nothing' ELSE 'test' END"),
        # Nested Case Expressions
        # https://github.com/alanmcruickshank/sqlfluff/issues/172
        ("ExpressionSegment",
         ("CASE WHEN id = 1 THEN CASE WHEN true THEN 'something' "
          "ELSE 'nothing' END ELSE 'test' END")),
        # Casting expressions
        # https://github.com/alanmcruickshank/sqlfluff/issues/161
        ("ExpressionSegment",
         "CAST(ROUND(online_sales / 1000.0) AS varchar)"),
        # Like expressions
        # https://github.com/alanmcruickshank/sqlfluff/issues/170
        ("ExpressionSegment",
         "name NOT LIKE '%y'"),
        # Functions with a space
        # https://github.com/alanmcruickshank/sqlfluff/issues/171
        ("SelectTargetElementSegment",
         "MIN (test.id) AS min_test_id"),
        # Interval literals
        # https://github.com/alanmcruickshank/sqlfluff/issues/148
        ("ExpressionSegment",
         "DATE_ADD(CURRENT_DATE('America/New_York'), INTERVAL 1 year)"),
        # Array accessors
        ("ExpressionSegment", "my_array[1]"),
        ("ExpressionSegment", "my_array[OFFSET(1)]"),
        ("ExpressionSegment", "my_array[5:8]"),
        ("ExpressionSegment", "4 + my_array[OFFSET(1)]"),
        ("ExpressionSegment", "bits[OFFSET(0)] + 7"),
        ("SelectTargetElementSegment",
         ("(count_18_24 * bits[OFFSET(0)])"
          " / audience_size AS relative_abundance")),
        ("ExpressionSegment",
         "count_18_24 * bits[OFFSET(0)] + count_25_34"),
        ("SelectTargetElementSegment",
         ("(count_18_24 * bits[OFFSET(0)] + count_25_34)"
          " / audience_size AS relative_abundance")),
        # Dense math expressions
        # https://github.com/alanmcruickshank/sqlfluff/issues/178
        # https://github.com/alanmcruickshank/sqlfluff/issues/179
        ("SelectStatementSegment", "SELECT t.val/t.id FROM test WHERE id*1.0/id > 0.8"),
        ("SelectTargetElementSegment", "t.val/t.id"),
        # Issue with casting raise as part of PR #177
        ("SelectTargetElementSegment",
         "CAST(num AS INT64)"),
        # Casting as datatype with arguments
        ("SelectTargetElementSegment",
         "CAST(num AS numeric(8,4))"),
        # Wildcard field selection
        ("SelectTargetElementSegment", "a.*"),
        ("SelectTargetElementSegment", "a.b.*"),
        ("SelectTargetElementSegment", "a.b.c.*"),
        # Default Element Syntax
        ("ObjectReferenceSegment", "a..c.*")
    ]
)
def test__dialect__ansi_specific_segment_parses(segmentref, raw, caplog):
    """Test that specific segments parse as expected.

    NB: We're testing the PARSE function not the MATCH function
    although this will be a recursive parse and so the match
    function of SUBSECTIONS will be tested if present. The match
    function of the parent will not be tested.
    """
    # Set up the lexer
    config = FluffConfig(overrides=dict(dialect='ansi'))
    lex = Lexer(config=config)
    c = ParseContext.from_config(config)
    # Lex the string for matching. For a good test, this would
    # arguably happen as a fixture, but it's easier to pass strings
    # as parameters than pre-lexed segment strings.
    seg_list, vs = lex.lex(raw)
    assert not vs

    print(seg_list)
    # Get the segment class for matching
    Seg = config.get('dialect_obj').ref(segmentref)
    if not issubclass(Seg, BaseSegment):
        raise TypeError("{0} is not of type Segment. Test is invalid.".format(segmentref))

    # This test is different if we're working with RawSegment
    # derivatives or not.
    if issubclass(Seg, RawSegment):
        print("Raw route...")
        with caplog.at_level(logging.DEBUG):
            parsed = Seg.match(segments=seg_list, parse_context=c)
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
        with caplog.at_level(logging.DEBUG):
            parsed = seg.parse(parse_context=c)
        print(parsed)
        assert isinstance(parsed, Seg)

    # Check we get a good response
    print(parsed)
    print(type(parsed))
    # print(type(parsed._reconstruct()))
    print(type(parsed.raw))
    # Check we're all there.
    assert parsed.raw == raw
    # Check that there's nothing un parsable
    typs = parsed.type_set()
    assert 'unparsable' not in typs
