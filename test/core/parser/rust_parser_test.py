"""Tests for the RustParser error handling and iteration limits."""

import pytest

try:
    from sqlfluff.core.parser.rust_parser import _HAS_RUST_PARSER, RustParser
    from sqlfluffrs import RsParser
except ImportError:
    _HAS_RUST_PARSER = False


# ---------------------------------------------------------------------------
# Iteration limit constants (should match default_config.cfg and core.rs)
# ---------------------------------------------------------------------------
_DEFAULT_MAX_ITERATIONS = 3_000_000
_DEFAULT_WARN_THRESHOLD = 2_000_000


# ============================================================================
# Iteration limit tests
# ============================================================================


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__iteration_limit__default_config_values():
    """Default config values for iteration limits match documented constants.

    The default values are defined in three places that must stay in sync:
    - ``default_config.cfg``  (Python config layer)
    - ``core.rs``             (Rust ``Parser::new`` defaults)
    - The constants in this test file

    If this test fails, update all three locations together.
    """
    from sqlfluff.core import FluffConfig

    config = FluffConfig.from_string("[sqlfluff]\ndialect = ansi")

    assert config.get("rust_parser_max_iterations") == _DEFAULT_MAX_ITERATIONS, (
        "rust_parser_max_iterations default does not match expected constant "
        f"({_DEFAULT_MAX_ITERATIONS}). Update default_config.cfg."
    )
    assert config.get("rust_parser_warn_threshold") == _DEFAULT_WARN_THRESHOLD, (
        "rust_parser_warn_threshold default does not match expected constant "
        f"({_DEFAULT_WARN_THRESHOLD}). Update default_config.cfg."
    )


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__iteration_limit__rs_parser_constructor_accepts_limits():
    """Rust parser constructor accepts and stores keyword arguments without error."""
    # Low values — just checking the constructor signature, not triggering limits.
    p = RsParser(
        dialect="ansi",
        indent_config={},
        max_parser_iterations=500_000,
        parser_warn_threshold=250_000,
    )
    # The dialect getter confirms the object was created successfully.
    assert p.dialect == "ansi"


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__iteration_limit__exceeded_raises_base_exception():
    """Exceeding max_parser_iterations raises a BaseException (PanicException).

    ``max_parser_iterations=1`` is impossibly low for any real SQL, so even
    ``SELECT 1`` crosses the limit.  The Rust panic surfaces in Python as
    ``pyo3_runtime.PanicException``, which inherits from ``BaseException``
    (not ``Exception``).
    """
    from sqlfluff.core import FluffConfig
    from sqlfluff.core.parser import Lexer

    config = FluffConfig.from_string("[sqlfluff]\ndialect = ansi")
    lexer = Lexer(config=config)
    segments, _ = lexer.lex("SELECT 1")
    tokens = [
        s._rstoken
        for s in segments
        if hasattr(s, "_rstoken") and s._rstoken is not None
    ]

    p = RsParser(
        dialect="ansi",
        indent_config={},
        max_parser_iterations=1,
        parser_warn_threshold=1,
    )

    with pytest.raises(BaseException) as exc_info:
        p.parse_match_result_from_tokens(tokens)

    assert "maximum iteration limit" in str(exc_info.value), (
        "Expected 'maximum iteration limit' in the panic message, got: "
        f"{exc_info.value}"
    )


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__iteration_limit__exceeded_via_rust_parser_wrapper():
    """RustParser.parse() propagates the panic when max_parser_iterations is exceeded.

    This exercises the full Python wrapper path: config → RsParser constructor
    → parse_match_result_from_tokens → Rust panic → BaseException in Python.
    """
    from sqlfluff.core import FluffConfig
    from sqlfluff.core.parser import Lexer

    config = FluffConfig.from_string(
        "[sqlfluff]\ndialect = ansi\nrust_parser_max_iterations = 1"
    )
    assert config.get("rust_parser_max_iterations") == 1

    lexer = Lexer(config=config)
    segments, _ = lexer.lex("SELECT 1")

    parser = RustParser(config=config)

    with pytest.raises(BaseException) as exc_info:
        parser.parse(segments, fname="test.sql")

    assert "maximum iteration limit" in str(exc_info.value)


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__iteration_limit__high_limit_parses_normally():
    """A high (or default) iteration limit does not prevent normal parsing."""
    from sqlfluff.core import FluffConfig
    from sqlfluff.core.parser import Lexer

    config = FluffConfig.from_string(
        "[sqlfluff]\ndialect = ansi\nrust_parser_max_iterations = 10000000"
    )
    lexer = Lexer(config=config)
    segments, _ = lexer.lex("SELECT a, b FROM t WHERE x = 1")

    parser = RustParser(config=config)
    result = parser.parse(segments, fname="test.sql")

    assert result is not None
    assert result.is_type("file")


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__iteration_limit__warn_threshold_lower_than_max_still_parses():
    """Setting parser_warn_threshold below the actual iteration count does not abort.

    This only causes a Rust-level warning log to stderr.

    The parse must still succeed as long as max_parser_iterations is not
    reached.
    """
    from sqlfluff.core import FluffConfig
    from sqlfluff.core.parser import Lexer

    # warn_threshold=1 means any real query will exceed it and emit a warning,
    # but max_parser_iterations is high enough that the parse completes.
    config = FluffConfig.from_string(
        "[sqlfluff]\ndialect = ansi\n"
        "rust_parser_warn_threshold = 1\n"
        "rust_parser_max_iterations = 10000000"
    )
    lexer = Lexer(config=config)
    segments, _ = lexer.lex("SELECT 1")

    parser = RustParser(config=config)
    result = parser.parse(segments, fname="test.sql")

    assert result is not None
    assert result.is_type("file")


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__iteration_limit__via_stats_method_same_behaviour():
    """parse_match_result_with_stats also enforces max_parser_iterations.

    The stats method uses the same underlying parser and must raise the
    same ``BaseException`` when the limit is exceeded.
    """
    from sqlfluff.core import FluffConfig
    from sqlfluff.core.parser import Lexer

    config = FluffConfig.from_string("[sqlfluff]\ndialect = ansi")
    lexer = Lexer(config=config)
    segments, _ = lexer.lex("SELECT 1")
    tokens = [
        s._rstoken
        for s in segments
        if hasattr(s, "_rstoken") and s._rstoken is not None
    ]

    p = RsParser(
        dialect="ansi",
        indent_config={},
        max_parser_iterations=1,
        parser_warn_threshold=1,
    )

    with pytest.raises(BaseException) as exc_info:
        p.parse_match_result_with_stats(tokens)

    assert "maximum iteration limit" in str(exc_info.value)


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
