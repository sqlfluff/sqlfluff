"""Tests for max_parse_depth limit (DoS mitigation)."""

import pytest

from sqlfluff.core import FluffConfig
from sqlfluff.core.errors import SQLParseError
from sqlfluff.core.linter.linter import Linter


# Limit low enough that very deep nesting triggers it, but above normal parse depth.
# Normal "SELECT 1" uses many grammar levels; we use 100 so simple SQL still parses.
MAX_DEPTH_LIMIT = 100
# Deep nesting to exceed the limit (each bracket adds depth).
NESTING_OVER_LIMIT = 120

MESSAGE_PREFIX = "Maximum parse depth exceeded"


def _linter_with_depth_limit(limit: int):
    """Linter with max_parse_depth set."""
    return Linter(
        config=FluffConfig(overrides={"dialect": "ansi", "max_parse_depth": limit})
    )


def test_max_parse_depth_exceeded_nested_brackets():
    """Deeply nested brackets exceed limit and raise SQLParseError."""
    linter = _linter_with_depth_limit(MAX_DEPTH_LIMIT)
    sql = "SELECT " + "(" * NESTING_OVER_LIMIT + "1" + ")" * NESTING_OVER_LIMIT
    parsed = linter.parse_string(sql)
    assert len(parsed.violations) >= 1
    err = parsed.violations[0]
    assert isinstance(err, SQLParseError)
    assert MESSAGE_PREFIX in err.desc()
    assert str(MAX_DEPTH_LIMIT) in err.desc()


def test_max_parse_depth_simple_sql_parses():
    """Simple SQL parses with default limit."""
    linter = Linter(config=FluffConfig(overrides={"dialect": "ansi"}))
    parsed = linter.parse_string("SELECT 1")
    assert not parsed.violations


def test_max_parse_depth_default_allows_simple_sql():
    """With default limit (255), simple SQL parses."""
    linter = Linter(config=FluffConfig(overrides={"dialect": "ansi"}))
    parsed = linter.parse_string("SELECT 1 FROM t")
    assert not parsed.violations


def test_max_parse_depth_rust_parser_exceeds_limit():
    """Rust parser respects max_parse_depth and raises same error (when available)."""
    try:
        from sqlfluff.core.parser.rust_parser import _HAS_RUST_PARSER, RustParser
    except ImportError:
        _HAS_RUST_PARSER = False

    if not _HAS_RUST_PARSER:
        pytest.skip("Rust parser not available")

    from sqlfluff.core.parser import Lexer

    config = FluffConfig(
        overrides={"dialect": "ansi", "max_parse_depth": MAX_DEPTH_LIMIT}
    )
    parser = RustParser(config=config)
    lexer = Lexer(config=config)
    sql = "SELECT " + "(" * NESTING_OVER_LIMIT + "1" + ")" * NESTING_OVER_LIMIT
    segments, _ = lexer.lex(sql)

    with pytest.raises(SQLParseError) as exc_info:
        parser.parse(segments, fname="test.sql")
    assert MESSAGE_PREFIX in exc_info.value.desc()
    assert str(MAX_DEPTH_LIMIT) in exc_info.value.desc()
