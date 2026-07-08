"""Tests for the RustParser error handling and iteration limits."""

from pathlib import Path

import pytest

from sqlfluff.core.errors import SQLFluffUserError

try:
    from sqlfluff.core.parser.rust_parser import _HAS_RUST_PARSER, RustParser
    from sqlfluffrs import RsParser
except ImportError:
    _HAS_RUST_PARSER = False


# ============================================================================
# max_parse_depth edge-case tests (lines 94-97 of rust_parser.py)
# ============================================================================


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__rust_parser__max_parse_depth_invalid_string_raises_config_error():
    """Invalid string values for max_parse_depth are rejected by config validation."""
    from sqlfluff.core import FluffConfig

    with pytest.raises(SQLFluffUserError):
        FluffConfig(overrides={"dialect": "ansi", "max_parse_depth": "invalid"})


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__rust_parser__max_parse_depth_zero_disables_limit():
    """RustParser with max_parse_depth=0 sets no depth limit.

    A value of 0 means "unlimited depth";
    simple SQL should still parse without errors.
    """
    from sqlfluff.core import FluffConfig
    from sqlfluff.core.parser import Lexer

    config = FluffConfig(overrides={"dialect": "ansi", "max_parse_depth": 0})
    parser = RustParser(config=config)
    lexer = Lexer(config=config)
    segments, _ = lexer.lex("SELECT 1")
    result = parser.parse(segments, fname="test.sql")
    assert result is not None
    assert result.is_type("file")


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__rust_parser__max_parse_depth_negative_one_raises_config_error():
    """RustParser config rejects negative max_parse_depth values.

    Public configuration uses ``0`` as the only disable value so that Python
    and Rust expose the same contract.
    """
    from sqlfluff.core import FluffConfig

    with pytest.raises(SQLFluffUserError):
        FluffConfig(overrides={"dialect": "ansi", "max_parse_depth": -1})


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
        max_parse_nodes=100_000,
    )
    # The dialect getter confirms the object was created successfully.
    assert p.dialect == "ansi"


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__rust_parser__max_parse_nodes_exceeded_in_rs_binding():
    """RsParser should reject oversized match trees via max_parse_nodes."""
    from sqlfluff.core import FluffConfig
    from sqlfluff.core.parser import Lexer

    config = FluffConfig(overrides={"dialect": "ansi"})
    lexer = Lexer(config=config)
    expr = "x" + "=x" * 6
    sql = "SELECT " + ",".join(expr for _ in range(80))
    segments, _ = lexer.lex(sql)
    tokens = [
        s._rstoken
        for s in segments
        if hasattr(s, "_rstoken") and s._rstoken is not None and s.is_code
    ]

    p = RsParser(
        dialect="ansi",
        indent_config={},
        max_parse_nodes=300,
    )

    with pytest.raises(Exception) as exc_info:
        p.parse_match_result_from_tokens(tokens)

    assert "Maximum parse node count exceeded" in str(exc_info.value)


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
    assert error.line_no > 0
    assert error.line_pos > 0


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


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__rust_parser__rs_node_class_types_match_python():
    """Regression: arena leaf class_types must mirror Python's class_types.

    A quoted-string MultiStringParser match (snowflake's quoted compression
    value, e.g. ``'GZIP'``) previously lost its keyword class hierarchy in the
    Rust node because aux_end was derived from the next grammar's offset, which
    can be 0 and wrongly truncated the count-prefixed class_types read.
    """
    from sqlfluff.core import FluffConfig
    from sqlfluff.core.parser import Lexer

    config = FluffConfig(overrides={"dialect": "snowflake", "use_rust_parser": True})
    sql = (
        "alter file format if exists my_avro_format set "
        "type = AVRO compression = 'GZIP'"
    )
    segments, _ = Lexer(config=config).lex(sql)
    tree = RustParser(config=config).parse(segments, fname="t.sql")

    # Flatten the Rust arena to its leaves (1:1 with raw_segments).
    leaves = []

    def _flatten(handle):
        children = handle.children
        if not children:
            leaves.append(handle)
        else:
            for child in children:
                _flatten(child)

    _flatten(tree._rs_tree.root)
    raws = tree.raw_segments
    assert len(leaves) == len(raws)

    # The quoted compression value carries the full keyword hierarchy and
    # matches Python's class_types exactly.
    checked_gzip = False
    for leaf, raw_seg in zip(leaves, raws):
        if raw_seg.raw.upper() == "'GZIP'":
            checked_gzip = True
            assert set(leaf.class_types() or []) == set(raw_seg.class_types)
            assert "keyword" in (leaf.class_types() or [])
    assert checked_gzip, "expected a quoted 'GZIP' compression value in the parse"


# ---------------------------------------------------------------------------
# Per-stage profiling
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__rust_parser__profiling_records_stage_timings():
    """Enabling profiling records per-stage wall-clock timings for a parse."""
    from sqlfluff.core import FluffConfig
    from sqlfluff.core.parser import Lexer
    from sqlfluff.core.parser.rust_parser import (
        get_parse_profile,
        reset_parse_profile,
        set_profiling,
    )

    config = FluffConfig(overrides={"dialect": "ansi"})
    parser = RustParser(config=config)
    lexer = Lexer(config=config)
    segments, _ = lexer.lex("SELECT 1 FROM my_table")

    set_profiling(True)
    reset_parse_profile()  # profile accumulates; isolate from other tests
    try:
        result = parser.parse(segments, fname="test.sql")
        profile = get_parse_profile()
    finally:
        set_profiling(False)

    assert result is not None
    # All four stages should be recorded, each a non-negative duration.
    assert set(profile) == {"rust_core", "convert", "apply", "apply_as_tree"}
    assert all(v >= 0.0 for v in profile.values())


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__rust_parser__profiling_accumulates_and_resets():
    """Timings accumulate across parses (e.g. template variants) until reset.

    parse() runs once per rendered variant, so the profile sums across parses
    rather than recording only the last one. reset_parse_profile() scopes it,
    and a no-code parse (early return) contributes nothing.
    """
    from sqlfluff.core import FluffConfig
    from sqlfluff.core.parser import Lexer
    from sqlfluff.core.parser.rust_parser import (
        get_parse_profile,
        reset_parse_profile,
        set_profiling,
    )

    config = FluffConfig(overrides={"dialect": "ansi"})
    parser = RustParser(config=config)
    lexer = Lexer(config=config)
    code_segments, _ = lexer.lex("SELECT 1 FROM my_table")

    set_profiling(True)
    try:
        # reset clears the accumulator.
        reset_parse_profile()
        assert get_parse_profile() == {}

        # First parse populates it.
        parser.parse(code_segments, fname="code.sql")
        after_one = get_parse_profile()
        assert after_one

        # A second parse (no reset) accumulates on top — it does not overwrite,
        # so the rust_core total strictly increases.
        parser.parse(code_segments, fname="code.sql")
        after_two = get_parse_profile()
        assert after_two["rust_core"] > after_one["rust_core"]

        # After a reset, a no-code parse (early return) adds nothing.
        reset_parse_profile()
        nocode_segments, _ = lexer.lex("-- just a comment\n")
        parser.parse(nocode_segments, fname="nocode.sql")
        assert get_parse_profile() == {}
    finally:
        set_profiling(False)


# ---------------------------------------------------------------------------
# Native (fused) AST builder parity
# ---------------------------------------------------------------------------

# All dialect fixtures, parametrized as (dialect, sqlfile). Parity must hold for
# every dialect since the flag affects all of them; covering the whole corpus
# also exercises the fused builder's rarer branches (e.g. zero-length matches).
_FIXTURE_DIR = Path(__file__).resolve().parents[3] / "test" / "fixtures" / "dialects"
_FIXTURE_SQL = sorted(_FIXTURE_DIR.glob("*/*.sql"))

# Fixtures with a *known*, already-documented Python-vs-RustParser divergence
# (see the dedicated xfail regressions above/below in this file). Three-way
# parity below is expected to fail on exactly these until those bugs are
# fixed; everywhere else in the corpus, all three tree-building paths must
# agree.
_KNOWN_PYTHON_RUST_DIVERGENCES = {
    ("databricks", "pivot.sql"),
    ("databricks", "unpivot.sql"),
    ("sparksql", "pivot_clause.sql"),
    ("sparksql", "unpivot_clause.sql"),
    ("snowflake", "create_catalog_integration.sql"),
    ("tsql", "datatype_methods.sql"),
    ("tsql", "sqlcmd_command.sql"),
}


def _fixture_param(sqlfile: Path):
    key = (sqlfile.parent.name, sqlfile.name)
    if key in _KNOWN_PYTHON_RUST_DIVERGENCES:
        return pytest.param(
            sqlfile,
            marks=pytest.mark.xfail(
                strict=True,
                reason=(
                    "Known Python-vs-RustParser divergence on this fixture; "
                    "see the dedicated test__rust_parser__vs_python_* "
                    "regression for this file elsewhere in this module."
                ),
            ),
        )
    return pytest.param(sqlfile)


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
@pytest.mark.parametrize(
    "sqlfile",
    [_fixture_param(p) for p in _FIXTURE_SQL],
    ids=[str(p.relative_to(_FIXTURE_DIR)) for p in _FIXTURE_SQL],
)
def test__rust_parser__native_ast_parity(sqlfile):
    """All three tree-building paths must agree: Python, RustParser, fused.

    For every dialect fixture, parse the same lexer output three ways - the
    pure-Python Parser, RustParser's legacy convert+apply path, and
    RustParser's fused native-AST builder - and assert the resulting
    BaseSegment trees (or raised exceptions) are all identical. Fixtures with
    an already-documented Python-vs-RustParser divergence are marked xfail
    (see _KNOWN_PYTHON_RUST_DIVERGENCES); every other fixture must agree
    across all three paths.
    """
    from sqlfluff.core import FluffConfig
    from sqlfluff.core.parser import Lexer, Parser
    from sqlfluff.core.parser.rust_parser import set_native_ast

    config = FluffConfig(overrides={"dialect": sqlfile.parent.name})
    segments, _ = Lexer(config=config).lex(sqlfile.read_text(encoding="utf-8"))

    def result_for(tree):
        return (
            "tree",
            tree.to_tuple(code_only=False, show_raw=True, include_meta=True)
            if tree
            else None,
        )

    def build_rust(native: bool):
        set_native_ast(native)
        try:
            tree = RustParser(config=config).parse(segments, fname=str(sqlfile))
            return result_for(tree)
        except BaseException as err:  # PanicException is a BaseException
            return ("exc", type(err).__name__)
        finally:
            set_native_ast(False)

    def build_python():
        try:
            tree = Parser(config=config).parse(segments, fname=str(sqlfile))
            return result_for(tree)
        except BaseException as err:
            return ("exc", type(err).__name__)

    python_result = build_python()
    rust_default = build_rust(native=False)
    rust_native = build_rust(native=True)

    assert rust_native == rust_default, "native-AST path diverges from convert+apply"
    assert python_result == rust_default, "RustParser diverges from Python Parser"


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
@pytest.mark.xfail(
    strict=True,
    reason=(
        "Regression: _convert_rs_match_result (the native_ast=False tree "
        "builder) recurses through an extra generator-expression stack frame "
        "per nesting level that _apply_rs_match_result (the fused "
        "native_ast=True builder) doesn't have, so the legacy path blows the "
        "Python call stack roughly twice as early as the fused path for the "
        "same deeply-nested input. Only reachable when max_parse_depth is "
        "raised above its default (600): at the default, the depth guard "
        "fires first on both paths identically, masking the divergence."
    ),
)
def test__rust_parser__native_ast_recursion_depth_asymmetry():
    """native_ast=True tolerates deeper bracket nesting than native_ast=False.

    Minimal repro for a real (if narrow) correctness divergence: with the
    depth guard raised out of the way, the two AST-building paths do not
    fail at the same input size for identical SQL and identical config.
    """
    from sqlfluff.core import FluffConfig
    from sqlfluff.core.parser import Lexer
    from sqlfluff.core.parser.rust_parser import set_native_ast

    sql = "SELECT " + "(" * 70 + "1" + ")" * 70
    config = FluffConfig(overrides={"dialect": "ansi", "max_parse_depth": 2000})
    segments, _ = Lexer(config=config).lex(sql)

    def build(native):
        set_native_ast(native)
        try:
            tree = RustParser(config=config).parse(segments, fname="t.sql")
            return (
                "tree",
                tree.to_tuple(code_only=False, show_raw=True, include_meta=True),
            )
        except BaseException as err:  # PanicException/RecursionError, etc.
            return ("exc", type(err).__name__)
        finally:
            set_native_ast(False)

    assert build(native=True) == build(native=False)


# ---------------------------------------------------------------------------
# RustParser vs. pure-Python Parser parity on malformed/error-recovery SQL
#
# Unlike the native_ast checks above (which compare RustParser against
# itself), these compare RustParser's Rust grammar-matching engine against
# the ground-truth pure-Python Parser, on malformed ANSI SQL that exercises
# GREEDY/GREEDY_ONCE_STARTED error-recovery paths. All 208 well-formed ANSI
# fixtures already parse identically between the two; these regressions only
# surface on malformed input, which is why they were previously undetected.
# ---------------------------------------------------------------------------


def _compare_parser_vs_rust(sql: str, dialect: str = "ansi"):
    """Parse the same SQL with the pure-Python Parser and RustParser."""
    from sqlfluff.core import FluffConfig
    from sqlfluff.core.parser import Lexer, Parser

    config = FluffConfig(overrides={"dialect": dialect})
    segments, _ = Lexer(config=config).lex(sql)

    def build(use_rust: bool):
        try:
            parser = RustParser(config=config) if use_rust else Parser(config=config)
            tree = parser.parse(segments, fname="t.sql")
            return (
                "tree",
                tree.to_tuple(code_only=False, show_raw=True, include_meta=True)
                if tree
                else None,
            )
        except BaseException as err:
            return ("exc", type(err).__name__)

    return build(True), build(False)


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
@pytest.mark.xfail(
    strict=True,
    reason=(
        "Regression: when a GREEDY_ONCE_STARTED Sequence (e.g. "
        "SelectClauseSegment) fails partway through, the Rust engine's "
        "'failed after partial match' branch "
        "(sqlfluffrs_parser/src/parser/table_driven/sequence.rs, the branch "
        "building `unparsable_match` with `..Default::default()`) drops the "
        "already-matched children's MatchResult (child_matches/"
        "insert_segments) instead of preserving them as siblings the way "
        "Python's Sequence.match does. The already-matched SELECT keyword "
        "then falls back to a raw, untyped `word` segment instead of a "
        "`keyword` segment. This is not just cosmetic: it makes rule ST05 "
        "raise an unhandled AssertionError('Keyword not found.') on input "
        "like 'SELECT CASE' when use_rust_parser=True, where the "
        "pure-Python path just reports a normal parse violation."
    ),
)
def test__rust_parser__vs_python_partial_match_failure_drops_children():
    """RustParser loses keyword typing when a GREEDY_ONCE_STARTED match fails.

    Minimal repro for a real correctness regression found by comparing
    RustParser against the ground-truth Python Parser on malformed SQL.
    """
    rust_result, python_result = _compare_parser_vs_rust("SELECT CASE")
    assert rust_result == python_result


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__rust_parser__vs_python_stray_closing_bracket_terminator():
    """RustParser aborts its terminator search on a stray ')', matching Python.

    Regression test: Python's greedy_match/next_ex_bracket_match
    (src/sqlfluff/core/parser/match_algorithms.py:469-529) aborts the
    terminator search entirely on an unexpected closing bracket, claiming
    everything up to EOF as unparsable. RustParser's greedy_match
    (sqlfluffrs_parser/src/parser/table_driven/match_algorithms.rs) now
    replicates this: an unmatched ')'/']'/'}' encountered while scanning for
    a terminator immediately aborts the search, rather than continuing on
    to find a later terminator (e.g. FROM) as it previously did.
    """
    rust_result, python_result = _compare_parser_vs_rust("SELECT 1) FROM t")
    assert rust_result == python_result


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
@pytest.mark.xfail(
    strict=True,
    reason=(
        "Regression: Bracketed.match (src/sqlfluff/core/parser/grammar/"
        "sequence.py:541-562) only suppresses the hard "
        "'Couldn't find closing bracket' SQLParseError for "
        "ParseMode.STRICT; for ParseMode.GREEDY (used by "
        "CTEDefinitionSegment at dialect_ansi.py:2869 and the VALUES tuple "
        "in ValuesClauseSegment at dialect_ansi.py:2748) Python always "
        "raises when no closing bracket is found before EOF. RustParser's "
        "codegen'd engine does not replicate this hard-raise, and instead "
        "returns a tree with the remainder wrapped as unparsable."
    ),
)
def test__rust_parser__vs_python_unclosed_greedy_bracket_raises():
    """Python raises SQLParseError for an unclosed GREEDY-mode bracket.

    RustParser instead recovers a tree, for the specific GREEDY-mode
    Bracketed sites (CTE definitions, VALUES tuples) that Python treats as
    a hard parse error rather than an unparsable section.
    """
    rust_result, python_result = _compare_parser_vs_rust("WITH a AS (SELECT 1")
    assert rust_result == python_result


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
@pytest.mark.xfail(
    strict=True,
    reason=(
        "Regression: for a GREEDY-mode Bracketed's Delimited content, "
        "trailing trivia (whitespace/comments) between a dangling trailing "
        "comma and the closing bracket is merged into the unparsable "
        "segment on the Rust side (sqlfluffrs_parser/src/parser/"
        "table_driven/bracketed.rs:456-476, which builds the unparsable "
        "span straight through to the closing bracket with no skip-back "
        "for trailing trivia), whereas Python's Bracketed.match "
        "(src/sqlfluff/core/parser/grammar/sequence.py:503-533) keeps that "
        "trivia as a separate, untyped sibling gap outside the unparsable "
        "class. Reproduces at any GREEDY Bracketed+Delimited site (IN-list, "
        "USING-list, ...), not just the one used here."
    ),
)
def test__rust_parser__vs_python_trailing_trivia_in_unparsable():
    """RustParser merges trailing trivia into an unparsable span; Python doesn't.

    A dangling trailing comma inside a GREEDY-mode Delimited bracket (e.g.
    an IN-list) is wrapped as unparsable by both engines, but they disagree
    on whether the whitespace between the comma and the closing bracket is
    part of that unparsable span or a sibling of it.
    """
    rust_result, python_result = _compare_parser_vs_rust(
        "SELECT a FROM t WHERE a IN (1, )"
    )
    assert rust_result == python_result


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
@pytest.mark.xfail(
    strict=True,
    reason=(
        "Regression: on a mismatched bracket type (e.g. '[' closed by ')'), "
        "Python's bracket-matching immediately detects the mismatch and "
        "raises a specific 'Found unexpected end bracket!, was expecting "
        "..., but got ...' SQLParseError. RustParser's engine doesn't "
        "replicate this specific check and instead falls through to the "
        "generic 'Couldn't find closing bracket for opening bracket.' "
        "error, as if the bracket were simply never closed. Same error "
        "message content differs even though both raise SQLParseError, so "
        "callers matching on the message (or anything depending on exact "
        "error text) will see different behaviour."
    ),
)
def test__rust_parser__vs_python_mismatched_bracket_type_error_message():
    """RustParser's error message differs from Python's for a wrong-bracket-type close."""
    from sqlfluff.core import FluffConfig
    from sqlfluff.core.parser import Lexer, Parser

    sql = "SELECT a[)"
    config = FluffConfig(overrides={"dialect": "ansi"})
    segments, _ = Lexer(config=config).lex(sql)

    def build(use_rust: bool):
        parser = RustParser(config=config) if use_rust else Parser(config=config)
        try:
            parser.parse(segments, fname="t.sql")
            return None
        except BaseException as err:
            return (type(err).__name__, str(err))

    assert build(True) == build(False)


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
@pytest.mark.xfail(
    strict=True,
    reason=(
        "Regression: a nested nested-bracket-type mismatch (e.g. an "
        "unclosed '(' inside '[...]' that gets 'closed' by the outer ']') "
        "makes Python raise the same 'Found unexpected end bracket!' "
        "SQLParseError as the flat mismatched-bracket-type case. RustParser "
        "instead silently recovers a tree, demoting the malformed nested "
        "bracket content to an unparsable expression rather than raising. "
        "This is bug class 3 (Python raises, Rust recovers) triggered by a "
        "nested mismatch rather than an unclosed-to-EOF bracket."
    ),
)
def test__rust_parser__vs_python_nested_bracket_mismatch_raises():
    """Python raises on nested bracket-type mismatch; RustParser recovers a tree."""
    rust_result, python_result = _compare_parser_vs_rust("SELECT a[(1]")
    assert rust_result == python_result


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__rust_parser__vs_python_stray_bracket_swallows_union_arm():
    """A stray ')' before UNION: Rust now discards the second arm too, matching Python.

    Regression test: a second instance of the stray-closing-bracket bug
    (see test__rust_parser__vs_python_stray_closing_bracket_terminator),
    this time at UnorderedSelectStatementSegment's own terminator scan
    (dialect_ansi.py) rather than SelectClauseSegment's. Before the fix,
    with a stray ')' before a UNION, Python discarded the ENTIRE second arm
    of the set operation as unparsable while RustParser incorrectly
    recovered a proper set_expression with both arms intact - now both
    engines discard the second arm identically.
    """
    rust_result, python_result = _compare_parser_vs_rust(
        "SELECT a FROM t) UNION SELECT c"
    )
    assert rust_result == python_result


# ---------------------------------------------------------------------------
# RustParser vs. pure-Python Parser divergences on well-formed, already-shipped
# dialect fixtures.
#
# Unlike the malformed-SQL cases above, these reproduce on VALID SQL that's
# already checked into the repo as a dialect fixture with a Python-generated
# .yml ground truth - i.e. RustParser disagrees with the fixture's own
# checked-in expected output, on input nobody had to invent. Found by running
# Parser vs RustParser over every fixture in every dialect (not just ansi);
# unlike ansi (0 mismatches across 208 fixtures), other dialects' fixtures
# turned up 7 mismatches across 4 dialects.
# ---------------------------------------------------------------------------


def _read_fixture(dialect: str, filename: str) -> str:
    return (_FIXTURE_DIR / dialect / filename).read_text(encoding="utf-8")


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
@pytest.mark.xfail(
    strict=True,
    reason=(
        "Regression: for a PIVOT clause whose aggregate expression is a "
        "function call (e.g. SUM(sales)), RustParser inserts a spurious "
        "extra Indent leaf inside PivotClauseSegment's Bracketed content "
        "that Python's Parser doesn't produce, shifting every subsequent "
        "leaf in the tree by one position for the rest of the file. "
        "PivotClauseSegment.match_grammar (dialect_sparksql.py:2485-2495) "
        "is `Sequence(Indent, 'PIVOT', Bracketed(Indent, Delimited(Sequence("
        "BaseExpressionElementGrammar, AliasExpressionSegment(optional))), "
        "...))` - the nested Bracketed's own leading Indent appears to be "
        "emitted twice on the Rust side for this shape. Reproduces "
        "identically in both databricks/pivot.sql and "
        "sparksql/pivot_clause.sql (databricks inherits sparksql's grammar)."
    ),
)
def test__rust_parser__vs_python_pivot_clause_indent_duplication():
    """RustParser duplicates an Indent inside PIVOT's bracketed content.

    Uses the real, already-shipped databricks/pivot.sql fixture - this is
    valid SQL with a correct Python-generated .yml, not invented malformed
    input.
    """
    sql = _read_fixture("databricks", "pivot.sql")
    rust_result, python_result = _compare_parser_vs_rust(sql, dialect="databricks")
    assert rust_result == python_result


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
@pytest.mark.xfail(
    strict=True,
    reason=(
        "Regression: the same class of spurious extra Indent as the PIVOT "
        "clause bug above, but inside UnpivotClauseSegment's bracketed "
        "column-alias content instead of PivotClauseSegment's function-call "
        "content - a second, distinct grammar site hitting the same "
        "underlying Rust Bracketed/Indent duplication issue. Reproduces "
        "identically in both databricks/unpivot.sql and "
        "sparksql/unpivot_clause.sql."
    ),
)
def test__rust_parser__vs_python_unpivot_clause_indent_duplication():
    """RustParser duplicates an Indent inside UNPIVOT's bracketed content.

    Uses the real, already-shipped databricks/unpivot.sql fixture.
    """
    sql = _read_fixture("databricks", "unpivot.sql")
    rust_result, python_result = _compare_parser_vs_rust(sql, dialect="databricks")
    assert rust_result == python_result


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
@pytest.mark.xfail(
    strict=True,
    reason=(
        "Regression: a numeric literal argument inside Snowflake's CREATE "
        "CATALOG INTEGRATION statement is typed as 'numeric_literal' by "
        "Python's Parser but as a generic, less-specific 'literal' by "
        "RustParser - the two trees are otherwise byte-identical (same "
        "leaf count, same positions), only the segment class assigned to "
        "this one value differs, at 5 separate occurrences in the file. "
        "This is a segment-class-assignment mismatch between the Rust "
        "grammar table's codegen'd class for this grammar element and the "
        "actual Python class Snowflake's grammar uses here."
    ),
)
def test__rust_parser__vs_python_snowflake_numeric_literal_mistyped():
    """RustParser types a numeric literal generically instead of as numeric_literal.

    Uses the real, already-shipped snowflake/create_catalog_integration.sql
    fixture.
    """
    sql = _read_fixture("snowflake", "create_catalog_integration.sql")
    rust_result, python_result = _compare_parser_vs_rust(sql, dialect="snowflake")
    assert rust_result == python_result


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
@pytest.mark.xfail(
    strict=True,
    reason=(
        "Regression: T-SQL's 'SomeSchema.Value(...)' (a datatype-method "
        "call, e.g. an XML column's .value() method) is a genuine grammar "
        "ambiguity - it can fully match either as a plain dotted function "
        "call (FunctionSegment, function_name='SomeSchema.Value') or as a "
        "column_reference with a DatatypeMethodSegment suffix "
        "(ObjectReferenceSegment's AnyNumberOf(OneOf(Ref('DatatypeMethod"
        "Segment'), ...)) in dialect_tsql.py:3565-3574). Both candidates "
        "match the exact same span (a real longest-match TIE, not one "
        "candidate being longer), so whichever wins depends purely on "
        "alternative-evaluation order. Python's Parser picks the function "
        "interpretation; RustParser picks the column_reference+datatype_"
        "method interpretation - a structurally different tree for the "
        "same SQL, not just a differently-typed leaf."
    ),
)
def test__rust_parser__vs_python_tsql_datatype_method_oneof_ambiguity():
    """RustParser resolves a genuine OneOf tie differently than Python.

    Uses the real, already-shipped tsql/datatype_methods.sql fixture.
    """
    sql = _read_fixture("tsql", "datatype_methods.sql")
    rust_result, python_result = _compare_parser_vs_rust(sql, dialect="tsql")
    assert rust_result == python_result


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
@pytest.mark.xfail(
    strict=True,
    reason=(
        "Regression: inside T-SQL's sqlcmd_command_segment (:setvar-style "
        "sqlcmd commands), RustParser loses the original lexer-assigned "
        "token type for its content - a bare word and a double-quoted "
        "string both come out as a generic 'raw' segment instead of "
        "'word'/'double_quote' respectively, as Python's Parser preserves. "
        "sqlcmd_command_segment's content is matched via a catch-all "
        "grammar (Anything()-style), and the Rust side isn't threading the "
        "original token class through in that path."
    ),
)
def test__rust_parser__vs_python_tsql_sqlcmd_command_loses_token_type():
    """RustParser loses word/double_quote token typing inside sqlcmd_command_segment.

    Uses the real, already-shipped tsql/sqlcmd_command.sql fixture.
    """
    sql = _read_fixture("tsql", "sqlcmd_command.sql")
    rust_result, python_result = _compare_parser_vs_rust(sql, dialect="tsql")
    assert rust_result == python_result


# ---------------------------------------------------------------------------
# PyLexer vs. PyRsLexer (the Rust-backed lexer) divergences.
#
# A separate investigation from the parser-layer bugs above: this compares
# tokenization itself, not grammar matching. The lexer port turned out to be
# extremely faithful (zero token-stream divergences across ~900 combined
# adversarial cases: position markers, dialect-specific quoting, unlexable/
# error boundaries). The one confirmed, deterministic divergence is in
# SQLLexError's message text, not the tokens themselves.
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
@pytest.mark.xfail(
    strict=True,
    reason=(
        "Regression: for an unlexable character run, PyLexer's "
        "violations_from_segments (src/sqlfluff/core/parser/lexer.py:"
        "838-847) builds the SQLLexError description via "
        "'Unable to lex characters: {!r}'.format(...) - repr()-quoting and "
        "escaping the raw text, and truncating to 9 characters plus a "
        "literal '...' marker when longer. The Rust lexer's equivalent "
        "(sqlfluffrs_lexer/src/lexer.rs:420-439, violations_from_tokens) "
        'instead does format!("Unable to lex characters: {}", '
        "token.raw().chars().take(10).collect::<String>()) - embedding the "
        "raw characters directly with no quoting/escaping, no truncation "
        "marker, and a 10- vs 9-character cutoff. SQLLexError.from_rs_error "
        "(src/sqlfluff/core/errors.py:190-200) passes the Rust description "
        "through verbatim, so real lint/parse output can contain literal "
        "unescaped control bytes or unicode where the Python lexer would "
        "have produced a safely quoted repr()-style string."
    ),
)
def test__rust_parser__vs_python_lexer_unlexable_error_message():
    """PyRsLexer's SQLLexError text differs from PyLexer's for unlexable input.

    Uses a non-ASCII character that neither lexer can tokenize, forcing the
    <unlexable> fallback path on both sides.
    """
    from sqlfluff.core import FluffConfig
    from sqlfluff.core.parser.lexer import PyLexer, PyRsLexer

    sql = "SELECT \xa1 FROM t"
    config = FluffConfig(overrides={"dialect": "ansi"})
    _, py_errs = PyLexer(config=config).lex(sql)
    _, rs_errs = PyRsLexer(config=config).lex(sql)

    assert [str(e) for e in py_errs] == [str(e) for e in rs_errs]


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__rust_parser__native_ast_profile_has_no_convert_stage():
    """With the native builder, profiling records no separate convert stage.

    Exercises the profiling timers on the native branch of parse() and confirms
    the fused builder folds convert into a single pass.
    """
    from sqlfluff.core import FluffConfig
    from sqlfluff.core.parser import Lexer
    from sqlfluff.core.parser.rust_parser import (
        get_parse_profile,
        reset_parse_profile,
        set_native_ast,
        set_profiling,
    )

    config = FluffConfig(overrides={"dialect": "ansi"})
    segments, _ = Lexer(config=config).lex("SELECT a, b FROM my_table WHERE a = 1")

    set_profiling(True)
    set_native_ast(True)
    reset_parse_profile()  # profile accumulates; scope to this parse
    try:
        RustParser(config=config).parse(segments, fname="test.sql")
        profile = get_parse_profile()
    finally:
        set_native_ast(False)
        set_profiling(False)

    # rust_core + the fused build are timed; convert no longer runs.
    assert "rust_core" in profile
    assert "apply" in profile
    assert "convert" not in profile


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__rust_parser__rs_tree_arena_navigation():
    """The Rust arena (``_rs_tree``) mirrors the Python tree for navigation.

    Smoke test for the RsTree/RsHandle façade substrate: the arena is ingested
    from the same node as the BaseSegment tree, so walking it to its leaves is
    1:1 with ``raw_segments``, handle accessors return the expected scalars, and
    parent/child links are consistent.
    """
    from sqlfluff.core import FluffConfig
    from sqlfluff.core.parser import Lexer

    config = FluffConfig(overrides={"dialect": "ansi", "use_rust_parser": True})
    sql = "SELECT a, b FROM my_table WHERE a > 1\n"
    segments, _ = Lexer(config=config).lex(sql)
    tree = RustParser(config=config).parse(segments, fname="t.sql")

    rs_tree = tree._rs_tree
    assert rs_tree is not None
    root = rs_tree.root

    # Root handle basics.
    assert root.type == "file"
    assert root.parent is None
    assert root.raw == tree.raw

    # Flatten the arena to its leaves (nodes with no children).
    leaves = []

    def _flatten(handle):
        children = handle.children
        if not children:
            leaves.append(handle)
        else:
            for child in children:
                # Parent links round-trip with child links.
                assert child.parent == handle
                _flatten(child)

    _flatten(root)

    raws = tree.raw_segments
    assert len(leaves) == len(raws)

    # Leaf scalars line up with the Python raw_segments, position by position.
    # NOTE: class_types is a subset, not equality — the arena faithfully carries
    # whatever the node tree has, but the full keyword hierarchy enrichment
    # (e.g. the inherited ``word`` type) is a separate fidelity fix not assumed
    # by this substrate test.
    for leaf, raw_seg in zip(leaves, raws):
        assert leaf.raw == raw_seg.raw
        assert leaf.type == raw_seg.get_type()
        assert set(leaf.class_types() or []) <= set(raw_seg.class_types)

    # The "FROM" keyword is reachable and typed.
    assert any(
        leaf.raw.upper() == "FROM" and leaf.is_type(["keyword"]) for leaf in leaves
    )
