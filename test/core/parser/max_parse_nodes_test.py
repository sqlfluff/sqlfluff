"""Tests for max_parse_nodes limit (DoS mitigation)."""

import pytest
from unittest.mock import patch

from sqlfluff.core import FluffConfig
from sqlfluff.core.errors import SQLParseError
from sqlfluff.core.linter.linter import Linter

MAX_NODE_LIMIT = 300
MESSAGE_PREFIX = "Maximum parse node count exceeded"


def _linter_with_node_limit(limit: int):
    """Linter with max_parse_nodes set, forcing the Python parser path."""
    return Linter(
        config=FluffConfig(
            overrides={
                "dialect": "ansi",
                "max_parse_nodes": limit,
                "use_rust_parser": False,
            }
        )
    )


def test_max_parse_nodes_default_allows_simple_sql():
    """Simple SQL should parse with the shipped default node limit."""
    linter = _linter_with_node_limit(100000)
    parsed = linter.parse_string("SELECT 1")
    assert not parsed.violations


def test_default_max_parse_nodes_matches_config_default():
    """FluffConfig exposes the shipped default max_parse_nodes value."""
    config = FluffConfig(overrides={"dialect": "ansi"})
    assert config.get("max_parse_nodes") == 100000


def test_max_parse_nodes_exceeded_wide_select_python_parser():
    """A wide select should exceed the configured node budget."""
    linter = _linter_with_node_limit(MAX_NODE_LIMIT)
    expr = "x" + "=x" * 6
    sql = "SELECT " + ",".join(expr for _ in range(80))

    parsed = linter.parse_string(sql)
    assert parsed.violations
    err = parsed.violations[0]
    assert isinstance(err, SQLParseError)
    assert MESSAGE_PREFIX in err.desc()
    assert str(MAX_NODE_LIMIT) in err.desc()
    assert err.segment is not None
    assert err.line_no > 0
    assert err.line_pos > 0


def test_max_parse_nodes_rust_parser_exceeds_limit():
    """Rust parser should surface the same node limit error when available."""
    try:
        from sqlfluff.core.parser.rust_parser import _HAS_RUST_PARSER, RustParser
    except ImportError:
        _HAS_RUST_PARSER = False

    if not _HAS_RUST_PARSER:
        pytest.skip("Rust parser not available")

    from sqlfluff.core.parser import Lexer

    config = FluffConfig(overrides={"dialect": "ansi", "max_parse_nodes": 300})
    parser = RustParser(config=config)
    lexer = Lexer(config=config)
    expr = "x" + "=x" * 6
    sql = "SELECT " + ",".join(expr for _ in range(80))
    segments, _ = lexer.lex(sql)

    with pytest.raises(SQLParseError) as exc_info:
        parser.parse(segments, fname="test.sql")
    assert MESSAGE_PREFIX in exc_info.value.desc()
    assert "300" in exc_info.value.desc()
    assert exc_info.value.segment is not None
    assert exc_info.value.line_no > 0
    assert exc_info.value.line_pos > 0


def test_validate_segment_with_reparse_respects_max_parse_nodes():
    """Segment reparse validation should use the node budget too."""
    linter = _linter_with_node_limit(100000)
    parsed = linter.parse_string("SELECT a, b, c FROM t")

    with pytest.raises(SQLParseError) as exc_info:
        parsed.tree.validate_segment_with_reparse(
            parsed.config.get("dialect_obj"),
            max_parse_depth=parsed.config.get("max_parse_depth"),
            max_parse_nodes=1,
        )

    assert MESSAGE_PREFIX in exc_info.value.desc()


def test_max_parse_nodes_token_gate_skips_python_parser():
    """The shared token gate should reject oversized token streams before parsing."""
    config = FluffConfig(
        overrides={
            "dialect": "ansi",
            "max_parse_nodes": MAX_NODE_LIMIT,
            "use_rust_parser": False,
        }
    )
    linter = Linter(config=config)
    expr = "x" + "=x" * 6
    sql = "SELECT " + ",".join(expr for _ in range(80))

    with patch("sqlfluff.core.parser.parser.Parser.parse") as parse_mock:
        parsed = linter.parse_string(sql)

    parse_mock.assert_not_called()
    assert parsed.violations
    err = parsed.violations[0]
    assert isinstance(err, SQLParseError)
    assert MESSAGE_PREFIX in err.desc()
    assert str(MAX_NODE_LIMIT) in err.desc()


def test_max_parse_nodes_token_gate_skips_rust_parser():
    """The shared token gate should also reject before the Rust parser starts."""
    try:
        from sqlfluff.core.parser.rust_parser import _HAS_RUST_PARSER
    except ImportError:
        _HAS_RUST_PARSER = False

    if not _HAS_RUST_PARSER:
        pytest.skip("Rust parser not available")

    config = FluffConfig(
        overrides={
            "dialect": "ansi",
            "max_parse_nodes": MAX_NODE_LIMIT,
            "use_rust_parser": True,
        }
    )
    linter = Linter(config=config)
    expr = "x" + "=x" * 6
    sql = "SELECT " + ",".join(expr for _ in range(80))

    with patch("sqlfluff.core.parser.rust_parser.RustParser.parse") as parse_mock:
        parsed = linter.parse_string(sql)

    parse_mock.assert_not_called()
    assert parsed.violations
    err = parsed.violations[0]
    assert isinstance(err, SQLParseError)
    assert MESSAGE_PREFIX in err.desc()
    assert str(MAX_NODE_LIMIT) in err.desc()