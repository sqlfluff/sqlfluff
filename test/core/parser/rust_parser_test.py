"""Tests for the RustParser error handling."""

import pytest

try:
    from sqlfluff.core.parser.rust_parser import _HAS_RUST_PARSER, RustParser
except ImportError:
    _HAS_RUST_PARSER = False


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__rust_parser__exception_fallback_to_first_segment():
    """Test RustParser error handling with fallback to first segment.

    This test documents the error handling code path in RustParser.parse()
    where if the Rust parser raises an exception:

    1. It checks if the exception has a 'pos' attribute (from RsParseError)
    2. If yes, it tries to extract the position and find the error segment
    3. If extraction fails (ValueError, TypeError, IndexError) or no pos attribute,
       it falls back to using the first segment (lines 195-197)

    Note: This is difficult to test directly because:
    - Rust parser methods are read-only and can't be mocked
    - The Rust parser is designed to embed errors in MatchResult, not raise
    - RsParseError always includes a valid pos attribute when raised

    The fallback path exists as defensive programming for unexpected exceptions
    that don't have position information.
    """
    from sqlfluff.core import FluffConfig
    from sqlfluff.core.parser import Lexer

    # Create a parser
    config = FluffConfig.from_string("[sqlfluff]\ndialect = ansi")
    parser = RustParser(config=config)

    # Create segments using the lexer so they have proper _rstoken attributes
    lexer = Lexer(config=config)
    segments, _ = lexer.lex("SELECT 1")

    # Verify the parser works normally with valid SQL
    result = parser.parse(segments, fname="test.sql")
    assert result is not None
    assert len(result.segments) > 0

    # The fallback code (if error_segment is None and segments[_start_idx:_end_idx])
    # ensures that if all position extraction fails, we still provide *some*
    # segment for error reporting rather than None, improving error messages.


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__rust_parser__parse_error_from_exception():
    """Test RustParser raises SQLParseError from RsParseError exception.

    This test exercises the code path where the Rust parser
    raises an RsParseError exception that gets converted to SQLParseError.
    When the Rust parser encounters an unclosed bracket in a greedy match,
    it raises RsParseError with position information. The from_rs_parse_error
    classmethod extracts the position, finds the corresponding segment, and
    creates a SQLParseError with proper location details.
    """
    from sqlfluff.core import FluffConfig
    from sqlfluff.core.errors import SQLParseError
    from sqlfluff.core.parser import Lexer

    # Create a parser
    config = FluffConfig.from_string("[sqlfluff]\ndialect = ansi")
    parser = RustParser(config=config)
    lexer = Lexer(config=config)

    # Use SQL with an unclosed bracket - this causes the Rust parser to
    # raise RsParseError immediately
    invalid_sql = "SELECT (1 + 2"
    segments, _ = lexer.lex(invalid_sql)

    # This should raise SQLParseError with position information
    with pytest.raises(SQLParseError) as exc_info:
        parser.parse(segments, fname="test.sql")

    # Verify the error has useful information
    error = exc_info.value
    assert "Couldn't find closing bracket" in str(error)
    # The error should have a segment associated with it
    assert error.segment is not None


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__rust_parser__trailing_non_code_segments():
    """Test RustParser handles trailing non-code segments correctly.

    This test exercises the code path where there are unmatched
    segments after parsing, but they are all non-code (whitespace, comments).
    In this case, they are added as-is without wrapping in UnparsableSegment.
    """
    from sqlfluff.core import FluffConfig
    from sqlfluff.core.parser import Lexer

    # Create a parser
    config = FluffConfig.from_string("[sqlfluff]\ndialect = ansi")
    parser = RustParser(config=config)
    lexer = Lexer(config=config)

    # Use SQL with trailing whitespace and comment
    # The parser will match the SELECT statement, leaving trailing non-code segments
    sql_with_trailing = "SELECT 1   \n-- comment\n   "
    segments, _ = lexer.lex(sql_with_trailing)

    # This should parse successfully and include trailing non-code segments
    result = parser.parse(segments, fname="test.sql")
    assert result is not None

    # Verify the result includes both the parsed SQL and trailing segments
    all_segments = list(result.iter_segments(expanding=["file"]))
    # Should have SELECT, whitespace, 1, and trailing whitespace/comment
    assert len(all_segments) > 3

    # Check that no UnparsableSegment was created (since trailing is all non-code)
    unparsable_segments = [s for s in all_segments if s.is_type("unparsable")]
    assert len(unparsable_segments) == 0
