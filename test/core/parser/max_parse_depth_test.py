"""Tests for max_parse_depth limit (DoS mitigation)."""

from typing import Callable

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
    assert err.segment is not None
    assert err.line_no > 0
    assert err.line_pos > 0


def test_max_parse_depth_simple_sql_parses():
    """Simple SQL parses with default limit."""
    linter = Linter(config=FluffConfig(overrides={"dialect": "ansi"}))
    parsed = linter.parse_string("SELECT 1")
    assert not parsed.violations


def test_max_parse_depth_default_allows_nested_function_calls():
    """Modestly nested function calls parse under the default limit (issue #7805).

    Uses the shipped default, since dialect fixtures parse at a depth of 1024 and
    wouldn't catch the default being too low.
    """
    sql = """CREATE FUNCTION [dbo].[fn_StringWithoutSpace]
(
    @string NVARCHAR(MAX)
)
RETURNS NVARCHAR(MAX)
WITH INLINE = OFF
AS
BEGIN
    RETURN (
        SELECT LTRIM(RTRIM(REPLACE(REPLACE(REPLACE(REPLACE(
            @string,
            CHAR(160), CHAR(32)),
            CHAR(32),  '()'),
            ')(',      ''),
            '()',      CHAR(32))))
    )
END
"""
    linter = Linter(config=FluffConfig(overrides={"dialect": "tsql"}))
    parsed = linter.parse_string(sql)
    assert not any(
        isinstance(v, SQLParseError) and MESSAGE_PREFIX in v.desc()
        for v in parsed.violations
    )


def test_max_parse_depth_default_allows_simple_sql():
    """With default limit (600), simple SQL parses."""
    linter = Linter(config=FluffConfig(overrides={"dialect": "ansi"}))
    parsed = linter.parse_string("SELECT 1 FROM t")
    assert not parsed.violations


def test_default_max_parse_depth_matches_config_default():
    """FluffConfig exposes the shipped default config value."""
    config = FluffConfig(overrides={"dialect": "ansi"})
    assert config.get("max_parse_depth") == 600


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
    assert exc_info.value.segment is not None
    assert exc_info.value.line_no > 0
    assert exc_info.value.line_pos > 0


def test_parse_context_max_parse_depth_zero_disables_limit():
    """ParseContext.from_config with max_parse_depth=0 disables the depth limit.

    A value of 0 is treated as "no limit",
    so from_config should set max_parse_depth to 0 on the context.
    """
    from sqlfluff.core.parser.context import ParseContext

    config = FluffConfig(overrides={"dialect": "ansi", "max_parse_depth": 0})
    ctx = ParseContext.from_config(config)
    assert ctx.max_parse_depth == 0


def _rust_parser_available() -> bool:
    """Whether the Rust parser extension is importable."""
    try:
        from sqlfluff.core.parser.rust_parser import _HAS_RUST_PARSER
    except ImportError:
        return False
    return bool(_HAS_RUST_PARSER)


def _engine_accepts_at_depth(sql: str, use_rust: bool, limit: int) -> bool:
    """Whether the engine parses ``sql`` under ``max_parse_depth=limit``."""
    config = FluffConfig(
        overrides={
            "dialect": "ansi",
            "use_rust_parser": use_rust,
            # Disable the node limit so only the depth guard is exercised.
            "max_parse_nodes": 0,
            "max_parse_depth": limit,
        }
    )
    parsed = Linter(config=config).parse_string(sql)
    return not any(
        isinstance(v, SQLParseError) and MESSAGE_PREFIX in v.desc()
        for v in parsed.violations
    )


def _depth_metric(sql: str, use_rust: bool, hi: int = 1500) -> int:
    """Smallest ``max_parse_depth`` at which the engine accepts ``sql``.

    The guard rejects when the tracked depth is strictly greater than the
    limit, so this equals the engine's peak tracked depth for the input.
    """
    assert _engine_accepts_at_depth(sql, use_rust, hi), "upper bound too low"
    lo = 1
    while lo < hi:
        mid = (lo + hi) // 2
        if _engine_accepts_at_depth(sql, use_rust, mid):
            hi = mid
        else:
            lo = mid + 1
    return lo


_DEPTH_SHAPES: list[tuple[str, Callable[[int], str]]] = [
    ("nested_brackets", lambda d: "SELECT " + "(" * d + "1" + ")" * d),
    ("nested_functions", lambda d: "SELECT " + "f(" * d + "1" + ")" * d),
    ("nested_subqueries", lambda d: "SELECT " + "(SELECT " * d + "1" + ")" * d),
    ("bracketed_arithmetic", lambda d: "SELECT " + "1+(" * d + "1" + ")" * d),
    ("flat_plus_chain", lambda d: "SELECT " + "+".join("1" for _ in range(d))),
]


@pytest.mark.skipif(not _rust_parser_available(), reason="Rust parser not available")
@pytest.mark.parametrize(
    "name,builder", _DEPTH_SHAPES, ids=[shape[0] for shape in _DEPTH_SHAPES]
)
def test_max_parse_depth_rust_is_never_stricter_than_python(
    name: str, builder: Callable[[int], str]
) -> None:
    """The Rust engine must not reject SQL that the Python engine accepts.

    The two engines count parse depth differently: Python tracks nested
    ``deeper_match`` contexts while Rust tracks its table-driven frame stack, so
    the exact boundary at which ``max_parse_depth`` trips is engine-dependent.
    Python is currently the stricter of the two. This test pins only the *safe*
    direction — Rust's threshold must not exceed Python's — so that the default
    (Rust) engine can never start rejecting input that pure Python would parse.
    Exact parity is a separate, tracked issue.
    """
    sql = builder(25)
    python_metric = _depth_metric(sql, use_rust=False)
    rust_metric = _depth_metric(sql, use_rust=True)
    assert rust_metric <= python_metric, (
        f"{name}: Rust depth threshold ({rust_metric}) exceeded Python's "
        f"({python_metric}); the default engine now rejects deeper input than "
        "pure Python, which is the unsafe direction."
    )
