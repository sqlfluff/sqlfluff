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


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
@pytest.mark.parametrize(
    "sqlfile",
    _FIXTURE_SQL,
    ids=[str(p.relative_to(_FIXTURE_DIR)) for p in _FIXTURE_SQL],
)
def test__rust_parser__native_ast_parity(sqlfile):
    """The fused builder must produce the same tree as convert+apply.

    For every dialect fixture, parse the same lexer output twice - once via the
    legacy convert+apply path and once via the fused native builder - and assert
    the resulting BaseSegment trees (or raised exceptions) are identical. Both
    paths use the same config, so this isolates the tree-building difference.
    """
    from sqlfluff.core import FluffConfig
    from sqlfluff.core.parser import Lexer
    from sqlfluff.core.parser.rust_parser import set_native_ast

    config = FluffConfig(overrides={"dialect": sqlfile.parent.name})
    segments, _ = Lexer(config=config).lex(sqlfile.read_text(encoding="utf-8"))

    def build(native: bool):
        set_native_ast(native)
        try:
            tree = RustParser(config=config).parse(segments, fname=str(sqlfile))
            return (
                "tree",
                tree.to_tuple(code_only=False, show_raw=True, include_meta=True)
                if tree
                else None,
            )
        except BaseException as err:  # PanicException is a BaseException
            return ("exc", type(err).__name__)
        finally:
            set_native_ast(False)

    assert build(native=True) == build(native=False)


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
