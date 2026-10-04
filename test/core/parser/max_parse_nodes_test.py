"""Tests for max_parse_nodes limit (DoS mitigation)."""

from pathlib import Path
from unittest.mock import patch

import pytest

from sqlfluff.core import FluffConfig
from sqlfluff.core.errors import SQLParseError
from sqlfluff.core.linter.linter import Linter

try:
    from sqlfluff.core.parser.rust_parser import _HAS_RUST_PARSER
except ImportError:  # pragma: no cover
    _HAS_RUST_PARSER = False

MAX_NODE_LIMIT = 300
MESSAGE_PREFIX = "Maximum parse node count exceeded"

# A synthesized reproduction of the accounting mismatch between the two
# engines. See the file header for the full story.
REPRO_FIXTURE = (
    Path(__file__).parents[2] / "fixtures" / "parser" / "max_parse_nodes_repro.sql"
)

# Limits chosen to straddle the fixture's node count (~5.4k), including points
# inside the band where the two engines used to disagree.
_PARITY_LIMITS = [4000, 4500, 5000, 5500, 6000]


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
    assert config.get("max_parse_nodes") == 200000


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


def _limit_exceeded(sql: str, use_rust_parser: bool, limit: int) -> bool:
    """Whether parsing ``sql`` with the given engine trips the node limit."""
    linter = Linter(
        config=FluffConfig(
            overrides={
                "dialect": "ansi",
                "use_rust_parser": use_rust_parser,
                "max_parse_nodes": limit,
            }
        )
    )
    parsed = linter.parse_string(sql)
    return any(MESSAGE_PREFIX in v.desc() for v in parsed.violations)


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
@pytest.mark.parametrize("limit", _PARITY_LIMITS)
def test_max_parse_nodes_python_rust_agree(limit):
    """The Python and Rust engines must enforce the node limit identically.

    Regression for the accounting mismatch where Python charged inserted
    segments only for zero-length matches while Rust charged them always, so
    the Rust engine rejected files the Python engine accepted just under the
    limit. The fixture is sized so that some of the parametrised limits fall
    inside the band the two engines used to disagree on.
    """
    sql = REPRO_FIXTURE.read_text()
    assert _limit_exceeded(sql, False, limit) == _limit_exceeded(sql, True, limit)


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test_max_parse_nodes_repro_fixture_parses_at_default():
    """The reproduction fixture parses under the shipped default on both engines."""
    sql = REPRO_FIXTURE.read_text()
    default = FluffConfig(overrides={"dialect": "ansi"}).get("max_parse_nodes")
    assert default == 200000
    assert not _limit_exceeded(sql, False, default)
    assert not _limit_exceeded(sql, True, default)
