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

# The whole-corpus three-way sweep (Python vs RustParser legacy vs fused
# native-AST) now lives in test/core/parser/parity/corpus_test.py, which
# captures at strictly higher strictness (position markers, stringify,
# class_types, normalization kwargs) than a to_tuple-only comparison here
# would - so it is not duplicated in this module.
_FIXTURE_DIR = Path(__file__).resolve().parents[3] / "test" / "fixtures" / "dialects"


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__rust_parser__native_ast_recursion_depth_asymmetry():
    """native_ast=True and native_ast=False now tolerate the same bracket nesting depth.

    _convert_rs_match_result (native_ast=False) and _apply_rs_match_result
    (native_ast=True) should fail at the same input size for identical SQL
    and config, since they should cost the same number of Python stack
    frames per nesting level. With max_parse_depth raised well above its
    default (600) so the depth guard doesn't mask the difference first,
    this checks the two paths stay in parity.

    NOTE: at this depth (70) both paths simply succeed - the interesting
    parity holds deeper too, confirmed manually: from ~140 bracket levels
    both raise a clean RecursionError (Python's own recursion-limit check,
    inside _apply_rs_match_result/_convert_rs_match_result), and from ~400
    both raise SQLParseError (the Rust matcher's own counted max_parse_depth
    check). There is also a narrow band (~120-140 bracket levels, with
    max_parse_depth raised this high) where the shared Rust grammar matcher
    overflows its native call stack and hard-crashes the process for both
    settings alike - unprotected by either language's recursion guard. That
    band isn't asserted here since its exact location is native-stack-size
    dependent (platform/OS/Rust build), not a stable cross-platform value;
    under the shipped default max_parse_depth (600) it's unreachable, since
    the counted guard trips at a much shallower physical depth first.
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
                tree.to_tuple(
                    code_only=False,
                    show_raw=True,
                    include_meta=True,
                    include_position=True,
                )
                if tree
                else None,
            )
        except BaseException as err:
            return (
                "exc",
                type(err).__name__,
                str(err),
                getattr(err, "line_no", None),
                getattr(err, "line_pos", None),
                getattr(err, "fatal", None),
                getattr(err, "ignore", None),
                getattr(err, "warning", None),
            )

    return build(True), build(False)


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__rust_parser__vs_python_partial_match_failure_drops_children():
    """RustParser preserves keyword typing when a GREEDY_ONCE_STARTED match fails.

    Regression test: when a GREEDY_ONCE_STARTED Sequence (e.g.
    SelectClauseSegment) fails partway through, the already-matched
    children (e.g. the SELECT keyword) must stay typed siblings, with only
    the unmatched tail wrapped as UnparsableSegment - matching Python's
    Sequence.match "handle the case of a partial match" behaviour.

    Previously, RustParser's "failed after partial match" branch in
    sqlfluffrs_parser/src/parser/table_driven/sequence.rs built its error
    MatchResult with `..Default::default()`, which silently dropped
    child_matches/insert_segments accumulated before the failure, so the
    already-matched SELECT keyword fell back to a raw, untyped `word`
    segment. This wasn't just cosmetic: it made rule ST05 raise an
    unhandled AssertionError('Keyword not found.') on input like
    'SELECT CASE' under use_rust_parser=True, where the pure-Python path
    just reported a normal parse violation.
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
        "Known gap: greedy_match's stray-closing-bracket check "
        "(sqlfluffrs_parser/src/parser/table_driven/match_algorithms.rs) "
        "recognises brackets by a hardcoded raw-text match on '(', '[', "
        "'{' and ')', ']', '}'. Python's equivalent, next_ex_bracket_match "
        "(src/sqlfluff/core/parser/match_algorithms.py:469-529), instead "
        "looks up the active dialect's bracket_pairs set, so it also "
        "recognises dialect-specific bracket tokens such as Snowflake's "
        "MATCH_RECOGNIZE exclude brackets '{-'/'-}' "
        "(dialect_snowflake.py:128-130). On a stray '-}', Python aborts the "
        "terminator search and claims the rest as unparsable, while Rust's "
        "hardcoded check doesn't recognise '-}' as a bracket at all and "
        "keeps scanning, finding the following FROM as a normal terminator. "
        "Fixing it means threading the dialect's bracket set through "
        "greedy_match instead of hardcoding ASCII brackets."
    ),
)
def test__rust_parser__vs_python_stray_closing_bracket_hardcoded_set():
    """RustParser's greedy_match only recognises a hardcoded ASCII bracket set.

    Snowflake's MATCH_RECOGNIZE exclude brackets ('{-'/'-}') are part of the
    dialect's bracket_pairs set, so Python treats a stray '-}' the same way
    as a stray ')'. RustParser's hardcoded check doesn't recognise '-}' as a
    bracket, so it keeps scanning past it instead of aborting.
    """
    rust_result, python_result = _compare_parser_vs_rust(
        "SELECT 1 -} FROM t", dialect="snowflake"
    )
    assert rust_result == python_result


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__rust_parser__vs_python_unclosed_greedy_bracket_raises():
    """Python and RustParser now agree: an unclosed GREEDY-mode bracket raises.

    Regression test for bracketed.rs: for ParseMode.GREEDY (used by
    CTEDefinitionSegment and the VALUES tuple in ValuesClauseSegment),
    Python's Bracketed.match() always raises SQLParseError when no closing
    bracket is found before EOF, so RustParser should raise too rather than
    quietly recovering an unparsable tree.
    """
    rust_result, python_result = _compare_parser_vs_rust("WITH a AS (SELECT 1")
    assert rust_result == python_result


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__rust_parser__vs_python_trailing_trivia_in_unparsable():
    """RustParser no longer merges trailing trivia into an unparsable span.

    Regression test: for a GREEDY-mode Bracketed's Delimited content, the
    trailing trivia (whitespace/comments) between a dangling trailing comma
    and the closing bracket used to be merged into the unparsable segment
    on the Rust side (Bracketed's own GREEDY-leftover detection built the
    unparsable span straight through to the closing bracket with no
    skip-back for trailing trivia), whereas Python's Bracketed.match keeps
    that trivia as a separate, untyped sibling gap outside the unparsable
    class. A dangling trailing comma inside a GREEDY-mode Delimited bracket
    (e.g. an IN-list) is wrapped as unparsable by both engines; they now
    agree on whether the whitespace between the comma and the closing
    bracket is part of that unparsable span or a sibling of it.
    """
    rust_result, python_result = _compare_parser_vs_rust(
        "SELECT a FROM t WHERE a IN (1, )"
    )
    assert rust_result == python_result


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__rust_parser__vs_python_mismatched_bracket_type_error_message():
    """RustParser now raises the same specific error as Python for a wrong-bracket-type close.

    Regression test: on a mismatched bracket type (e.g. '[' closed by ')'),
    Python's bracket-matching immediately detects the mismatch and raises a
    specific 'Found unexpected end bracket!, was expecting ..., but got
    ...' SQLParseError. RustParser's greedy_match used to fall through to
    the generic 'Couldn't find closing bracket for opening bracket.' error
    instead, as if the bracket were simply never closed - it now scans
    forward to distinguish a genuinely-unclosed bracket from one closed by
    the wrong type, matching Python's specific message.
    """
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
def test__rust_parser__vs_python_nested_bracket_mismatch_raises():
    """Python and RustParser agree on a nested bracket-type mismatch.

    A nested bracket-type mismatch (e.g. an unclosed '(' inside '[...]'
    that gets "closed" by the outer ']') should raise 'Found unexpected
    end bracket!' (SQLParseError) in both engines: `compute_bracket_pairs`
    requires a closer to match the innermost (top-of-stack) opener, per
    LIFO nesting discipline, matching Python's recursive `resolve_bracket`,
    which only ever resolves the innermost open bracket next.

    Both `compute_bracket_pairs` implementations enforce this:
    `sqlfluffrs_lexer/src/lexer.rs` (used when sqlfluffrs does its own
    lexing) and the duplicate in `sqlfluffrs_parser/src/parser/python.rs`
    (used when RustParser re-derives bracket pairs from Python-lexed
    tokens, e.g. via `Linter(use_rust_parser=True)` - the only publicly
    observable path).
    """
    rust_result, python_result = _compare_parser_vs_rust("SELECT a[(1]")
    assert rust_result == python_result


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
@pytest.mark.parametrize(
    "sql",
    [
        "SELECT a[(1]) ]",
        "SELECT a[[1)]]",
    ],
)
def test__rust_parser__vs_python_crossed_bracket_after_mismatch_raises(sql):
    """A later crossed bracket pair must not "recover" a mismatch, matching Python.

    Once a bracket-type mismatch occurs, every bracket that was still open
    at that point should stay unresolved, even if a later closer would
    otherwise cross-match one of them. This mirrors Python's recursive
    resolve_bracket: raising on the first mismatch unwinds through every
    enclosing bracket's own call, so none of them can be validly resolved
    afterwards. Both `compute_bracket_pairs` implementations enforce this
    by clearing the entire bracket stack (not just the mismatched pair)
    once a mismatch is found.
    """
    rust_result, python_result = _compare_parser_vs_rust(sql)
    assert rust_result == python_result


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__rust_parser__vs_python_unclosed_nested_bracket_error_position():
    """An unclosed bracket nested inside another should be blamed, not its parent.

    For brackets unclosed to EOF and nested two or more levels deep (e.g.
    an unclosed '(' containing an unclosed '['), the "couldn't find closing
    bracket" error should point at the innermost open bracket. This matches
    Python's resolve_bracket, which recurses into each opening bracket and
    raises from that recursive call once it reaches EOF.
    """
    rust_result, python_result = _compare_parser_vs_rust("SELECT a(b[1")
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
def test__rust_parser__vs_python_pivot_clause_indent_duplication():
    """RustParser must not duplicate an Indent inside PIVOT's bracketed content.

    Regression guard: RustParser used to emit the grammar-level Indent that
    is a direct child of PivotClauseSegment's Bracketed (dialect_sparksql.py
    `Bracketed(Indent, ...)`) in addition to Bracketed's own structural
    Indent, where Python drops the grammar-level one - shifting every
    subsequent leaf in the tree for the rest of the file. Fixed by dropping
    direct-child metas in the Rust Bracketed handler.

    Uses the real, already-shipped databricks/pivot.sql fixture - this is
    valid SQL with a correct Python-generated .yml, not invented malformed
    input.
    """
    sql = _read_fixture("databricks", "pivot.sql")
    rust_result, python_result = _compare_parser_vs_rust(sql, dialect="databricks")
    assert rust_result == python_result


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__rust_parser__vs_python_unpivot_clause_indent_duplication():
    """RustParser must not duplicate an Indent inside UNPIVOT's bracketed content.

    Regression guard: the same class of spurious extra Indent as the PIVOT
    clause case above, but inside UnpivotClauseSegment's bracketed
    column-alias content - a second, distinct grammar site of the same
    Rust Bracketed direct-child-meta issue.

    Uses the real, already-shipped databricks/unpivot.sql fixture.
    """
    sql = _read_fixture("databricks", "unpivot.sql")
    rust_result, python_result = _compare_parser_vs_rust(sql, dialect="databricks")
    assert rust_result == python_result


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__rust_parser__vs_python_snowflake_numeric_literal_mistyped():
    """RustParser now types this numeric literal as numeric_literal, matching Python.

    Regression test: `Ref("LiteralSegment")` (dialect_snowflake.py) targets
    a bare segment class with no dialect-specific match_grammar, so
    Python's isinstance fast path returns the already-lexed "10" token
    unwrapped, preserving its lex-time "numeric_literal" type.
    RustParser's `handle_ref_combining` (ref_grammar.rs) used to wrap the
    matched token in the grammar's class, re-typing it to the generic
    "literal" default. It now mirrors native `BaseSegment.match`: a Ref to
    a bare (match_grammar-less) class consumes the token UNCHANGED, so its
    lexer-assigned type and full class chain are preserved.

    Uses the real, already-shipped snowflake/create_catalog_integration.sql
    fixture.
    """
    sql = _read_fixture("snowflake", "create_catalog_integration.sql")
    rust_result, python_result = _compare_parser_vs_rust(sql, dialect="snowflake")
    assert rust_result == python_result


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__rust_parser__vs_python_tsql_datatype_method_oneof_ambiguity():
    """RustParser must agree with Python on T-SQL datatype-method SQL.

    Regression guard: RustParser used to compile every RegexParser pattern
    case-insensitively, ignoring ``ignore_case=False``. T-SQL's
    DatatypeMethodNameIdentifierSegment regex is deliberately
    case-sensitive (datatype methods are lowercase-only), and it is also
    the ``exclude`` on T-SQL's FunctionNameIdentifierSegment - so
    'SomeSchema.Value(...)' wrongly matched as a datatype method on the
    Rust side while the function interpretation Python picks was excluded,
    producing a structurally different tree. With case sensitivity
    honoured, both parsers agree.

    Uses the real, already-shipped tsql/datatype_methods.sql fixture.
    """
    sql = _read_fixture("tsql", "datatype_methods.sql")
    rust_result, python_result = _compare_parser_vs_rust(sql, dialect="tsql")
    assert rust_result == python_result


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__rust_parser__vs_python_tsql_sqlcmd_command_loses_token_type():
    """RustParser now preserves word/double_quote token typing inside sqlcmd_command_segment.

    Regression test: inside T-SQL's sqlcmd_command_segment (:setvar-style
    sqlcmd commands), RustParser used to lose the original lexer-assigned
    token type for its content - a bare word and a double-quoted string
    both came out as a generic 'raw' segment instead of
    'word'/'double_quote' respectively, as Python's Parser preserves.

    Same root cause and fix as
    test__rust_parser__vs_python_snowflake_numeric_literal_mistyped: a
    `Ref` to a bare segment class hits Python's isinstance fast path, so
    the matched token is now consumed UNCHANGED (no class wrap, no
    re-mint), preserving its lexer-assigned type and full class chain.

    Uses the real, already-shipped tsql/sqlcmd_command.sql fixture.
    """
    sql = _read_fixture("tsql", "sqlcmd_command.sql")
    rust_result, python_result = _compare_parser_vs_rust(sql, dialect="tsql")
    assert rust_result == python_result


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
@pytest.mark.parametrize(
    "dialect,sql",
    [
        # A numeric value routes a LiteralSegment (class chain includes the
        # class-level `literal`) through the bare `Ref("CodeSegment")` that
        # matches :setvar content - an ANCESTOR of the token's class.
        ("tsql", ":setvar count 10"),
        # The shipped fixture's quoted/word values are CodeSegment instances
        # directly, so they were always safe - kept here as a control.
        ("tsql", ':setvar count "variable_value"'),
        # Snowflake numeric literal via a bare `LiteralSegment` reference.
        (
            "snowflake",
            "CREATE CATALOG INTEGRATION glue_int CATALOG_SOURCE = GLUE "
            "REFRESH_INTERVAL_SECONDS = 10;",
        ),
    ],
)
def test__rust_parser__vs_python_bare_class_ref_preserves_class_types(dialect, sql):
    """A bare-class ``Ref`` must preserve the token's FULL class_types chain.

    Guards a blind spot: ``to_tuple`` (used by ``_compare_parser_vs_rust``)
    only records each leaf's ``get_type()``, not its ``class_types`` set.
    When a bare-class ``Ref`` targets an ANCESTOR of the matched token's
    class (e.g. ``Ref("CodeSegment")`` over a ``LiteralSegment`` numeric
    value in ``:setvar count 10``), an earlier fix that rebuilt the chain
    as ``ancestor-class ∪ instance_types`` produced the right ``get_type()``
    but silently dropped the class-level type (here ``literal``) - invisible
    to a ``to_tuple`` comparison. Bare-class grammars now consume the token
    unchanged, so its native ``class_types`` is preserved exactly.
    """
    from sqlfluff.core import FluffConfig
    from sqlfluff.core.parser import Lexer, Parser

    config = FluffConfig(overrides={"dialect": dialect})
    segments, _ = Lexer(config=config).lex(sql)
    python_tree = Parser(config=config).parse(segments, fname="t.sql")
    rust_tree = RustParser(config=config).parse(segments, fname="t.sql")

    def leaves(tree):
        return [s for s in tree.recursive_crawl_all() if not s.segments]

    for py_leaf, rs_leaf in zip(leaves(python_tree), leaves(rust_tree), strict=True):
        assert set(rs_leaf.class_types) == set(py_leaf.class_types), (
            f"class_types diverge for {py_leaf.raw!r}: "
            f"python={sorted(set(py_leaf.class_types))} "
            f"rust={sorted(set(rs_leaf.class_types))}"
        )


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
def test__rust_parser__vs_python_lexer_unlexable_error_message():
    """PyRsLexer's SQLLexError text now matches PyLexer's for unlexable input.

    Regression test: for an unlexable character run, PyLexer's
    violations_from_segments (src/sqlfluff/core/parser/lexer.py:838-847)
    builds the SQLLexError description via
    'Unable to lex characters: {!r}'.format(...) - repr()-quoting and
    escaping the raw text, and truncating to 9 characters plus a literal
    '...' marker when longer. The Rust lexer's equivalent
    (sqlfluffrs_lexer/src/lexer.rs, violations_from_tokens) used to embed
    the raw characters directly with no quoting/escaping, no truncation
    marker, and a 10- vs 9-character cutoff. SQLLexError.from_rs_error
    (src/sqlfluff/core/errors.py:190-200) passes the Rust description
    through verbatim, so real lint/parse output could contain literal
    unescaped control bytes or unicode where the Python lexer would have
    produced a safely quoted repr()-style string.

    Fixed by adding python_repr_str/truncate_like_python helpers in
    lexer.rs that replicate Python's repr()-quoting (quote-character
    selection, backslash/quote/control-character escaping) and the
    9-character truncation-plus-"..." cutoff. Uses a non-ASCII character
    that neither lexer can tokenize, forcing the <unlexable> fallback
    path on both sides.
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


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
@pytest.mark.parametrize(
    "method,is_datatype_method",
    [
        ("value", True),  # T-SQL data-type methods are case-SENSITIVE (lowercase)
        ("query", True),
        ("VALUE", False),  # upper/mixed case is NOT a data-type method
        ("Value", False),
        ("QUERY", False),
    ],
)
def test__rust_parser__tsql_datatype_method_case_sensitive(method, is_datatype_method):
    """Rust parser honors ``ignore_case=False``.

    ``col.value(...)`` is a data-type method (case-sensitive, lowercase only);
    ``col.VALUE(...)`` / ``col.Value(...)`` are not. The Rust parser must match
    native here.
    """
    from sqlfluff.core import FluffConfig, Linter

    src = f"SELECT col.{method}('/x', 'y') FROM t;\n"

    def method_ids(rust: bool):
        cfg = FluffConfig(
            overrides={
                "dialect": "tsql",
                "use_rust_parser": rust,
                "use_rust_engine": False,
            }
        )
        tree = Linter(config=cfg).parse_string(src).tree
        return [s.raw for s in tree.recursive_crawl("datatype_method_name_identifier")]

    rust_ids = method_ids(True)
    native_ids = method_ids(False)
    assert rust_ids == native_ids  # parity with native
    assert (method in rust_ids) is is_datatype_method
