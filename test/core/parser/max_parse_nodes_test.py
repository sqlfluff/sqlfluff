"""Tests for max_parse_nodes limit (DoS mitigation)."""

from unittest.mock import patch

import pytest

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


def _wide_select_sql() -> str:
    expr = "x" + "=x" * 6
    return "SELECT " + ",".join(expr for _ in range(80))


def _assert_node_limit_error(err: SQLParseError, limit: int) -> None:
    assert MESSAGE_PREFIX in err.desc()
    assert str(limit) in err.desc()
    assert err.segment is not None
    assert err.line_no > 0
    assert err.line_pos > 0


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
    sql = _wide_select_sql()

    parsed = linter.parse_string(sql)
    assert parsed.violations
    err = parsed.violations[0]
    assert isinstance(err, SQLParseError)
    _assert_node_limit_error(err, MAX_NODE_LIMIT)


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
    sql = _wide_select_sql()
    segments, _ = lexer.lex(sql)

    with pytest.raises(SQLParseError) as exc_info:
        parser.parse(segments, fname="test.sql")
    _assert_node_limit_error(exc_info.value, 300)


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


def test_parse_context_reads_max_parse_nodes_from_config():
    """ParseContext.from_config should load the configured node limit."""
    from sqlfluff.core.parser.context import ParseContext

    config = FluffConfig(overrides={"dialect": "ansi", "max_parse_nodes": 1234})
    ctx = ParseContext.from_config(config)
    assert ctx.max_parse_nodes == 1234


def test_parse_context_max_parse_nodes_zero_disables_limit():
    """ParseContext.from_config with max_parse_nodes=0 disables the node limit."""
    from sqlfluff.core.parser.context import ParseContext

    config = FluffConfig(overrides={"dialect": "ansi", "max_parse_nodes": 0})
    ctx = ParseContext.from_config(config)
    ctx.seed_parse_nodes(1000)
    ctx.increment_parse_nodes(1000)
    assert ctx.current_parse_nodes == 2000


def test_parse_context_seed_parse_nodes_raises_on_limit():
    """Seeding the node budget should enforce the configured limit."""
    from sqlfluff.core.parser.context import ParseContext

    ctx = ParseContext(dialect=None, max_parse_depth=0, max_parse_nodes=3)
    with pytest.raises(SQLParseError) as exc_info:
        ctx.seed_parse_nodes(4)
    assert MESSAGE_PREFIX in exc_info.value.desc()
    assert "3" in exc_info.value.desc()


def test_parse_context_increment_parse_nodes_raises_on_limit():
    """Incrementing parse nodes should enforce the configured limit."""
    from sqlfluff.core.parser.context import ParseContext

    ctx = ParseContext(dialect=None, max_parse_depth=0, max_parse_nodes=3)
    ctx.seed_parse_nodes(2)
    with pytest.raises(SQLParseError) as exc_info:
        ctx.increment_parse_nodes(2)
    assert MESSAGE_PREFIX in exc_info.value.desc()
    assert "3" in exc_info.value.desc()


@pytest.mark.parametrize(
    ("use_rust_parser", "patch_target"),
    [
        (False, "sqlfluff.core.parser.parser.Parser.parse"),
        pytest.param(
            True,
            "sqlfluff.core.parser.rust_parser.RustParser.parse",
            marks=pytest.mark.skipif(
                not __import__(
                    "sqlfluff.core.parser.rust_parser", fromlist=["_HAS_RUST_PARSER"]
                )._HAS_RUST_PARSER,
                reason="Rust parser not available",
            ),
        ),
    ],
)
def test_max_parse_nodes_token_gate_skips_parser(use_rust_parser, patch_target):
    """The shared token gate should reject oversized token streams before parsing."""
    config = FluffConfig(
        overrides={
            "dialect": "ansi",
            "max_parse_nodes": MAX_NODE_LIMIT,
            "use_rust_parser": use_rust_parser,
        }
    )
    linter = Linter(config=config)
    sql = _wide_select_sql()

    with patch(patch_target) as parse_mock:
        parsed = linter.parse_string(sql)

    parse_mock.assert_not_called()
    assert parsed.violations
    err = parsed.violations[0]
    assert isinstance(err, SQLParseError)
    _assert_node_limit_error(err, MAX_NODE_LIMIT)
