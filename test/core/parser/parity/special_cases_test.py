"""Parity tests that need Python-side instrumentation.

Most parity coverage is data-driven (see ``cases_test.py`` and
``test/fixtures/parity/``). The tests here instrument the Python side
instead: log capture, parse-node accounting hooks, shared-instance state,
subprocess hash-seed probes. They still use the shared capture machinery
from ``compare.py`` wherever a comparison is made.
"""

import sys

import pytest

from .compare import (
    _exception_capture,
    _tree_capture,
    build_config,
    parse_capture,
    requires_rust_parser,
)

try:
    from sqlfluff.core.parser.rust_parser import RustParser
except ImportError:  # pragma: no cover
    RustParser = None


def _native_and_legacy(sql, dialect="ansi", configs=None):
    """Capture the same lexed SQL through both RustParser build paths."""
    from sqlfluff.core.parser import Lexer

    config = build_config(dialect=dialect, configs=configs)
    segments, _ = Lexer(config=config).lex(sql)
    return (
        parse_capture("rust-native", config, segments),
        parse_capture("rust", config, segments),
    )


@requires_rust_parser
def test__parity__native_ast_recursion_depth_parity():
    """Both tree-building paths tolerate the same bracket-nesting depth.

    Regression test: the legacy tree builder (_convert_rs_match_result) used
    an extra generator-expression stack frame per nesting level that the
    fused builder (_apply_rs_match_result) avoids, so the legacy path hit
    the Python recursion limit roughly twice as early as the fused path on
    the same deeply-nested input. With the depth guard raised out of the
    way (max_parse_depth=2000; at the default of 600 the depth guard fires
    first on both paths at the same depth, hiding the difference), 70
    levels of bracket nesting built a tree on the fused path while the
    legacy path raised RecursionError. The converter now builds child
    matches with an explicit loop (one interpreter frame per level, matching
    MatchResult.apply and the fused builder), so both paths now succeed at
    this depth and keep failing together (both raising RecursionError) at
    much deeper nesting, once they share the same stack budget.
    """
    sql = "SELECT " + "(" * 70 + "1" + ")" * 70
    native_capture, legacy_capture = _native_and_legacy(
        sql, configs={"max_parse_depth": 2000}
    )
    assert native_capture == legacy_capture
    # Depth 70 fits comfortably within the shared stack budget, so the
    # parity above should come from both paths building the tree.
    assert legacy_capture[0] == "tree"


@requires_rust_parser
def test__parity__native_ast_alternating_modes_shared_instance():
    """Alternating build paths on one parser instance stays stable.

    Both paths share per-instance state (the _get_segment_class_by_name
    lru_cache, the RsParser handle) and module-global state (the native_ast
    flag). Parsing the same lexed segments repeatedly while flipping the flag
    gives the same result every time, keeping each mode's cache and state
    independent of the other.
    """
    from sqlfluff.core.parser import Lexer
    from sqlfluff.core.parser.rust_parser import set_native_ast

    config = build_config()
    parser = RustParser(config=config)
    lexer = Lexer(config=config)
    for sql in (
        "SELECT a FROM t",
        "SELECT CASE",
        "WITH x AS (SELECT 1) SELECT * FROM x",
    ):
        segments, _ = lexer.lex(sql)
        results = []
        for native in (False, True, False, True):
            set_native_ast(native)
            try:
                tree = parser.parse(segments, fname="t.sql")
                results.append(("none",) if tree is None else _tree_capture(tree))
            except BaseException as err:
                results.append(_exception_capture(err))
            finally:
                set_native_ast(False)
        assert all(r == results[0] for r in results), sql


@requires_rust_parser
def test__parity__native_ast_root_match_logging_parity(caplog):
    r"""Both build paths emit identical parser INFO diagnostics.

    Regression test: the fused native-AST builder used to skip the legacy
    path's ``parser_logger.info("Root Match:\\n%s", match)`` diagnostic
    entirely, so parsing the same SQL with parser logging enabled (e.g.
    ``sqlfluff parse -vvvv``) produced different diagnostics depending on
    the native_ast flag. The native path now emits the same record,
    building the intermediate MatchResult it needs for the message only when
    INFO logging is actually enabled (keeping the fused path free of
    conversion work during normal operation - see
    test__rust_parser__native_ast_profile_has_no_convert_stage).
    """
    import logging

    from sqlfluff.core.parser import Lexer
    from sqlfluff.core.parser.rust_parser import set_native_ast

    config = build_config()
    segments, _ = Lexer(config=config).lex("SELECT a, b FROM t WHERE a = 1")

    def parser_log_messages(native):
        caplog.clear()
        set_native_ast(native)
        try:
            with caplog.at_level(logging.INFO, logger="sqlfluff.parser"):
                RustParser(config=config).parse(segments, fname="t.sql")
        finally:
            set_native_ast(False)
        return [rec.getMessage() for rec in caplog.records]

    legacy_messages = parser_log_messages(native=False)
    native_messages = parser_log_messages(native=True)

    # The legacy path logs the root match; the native path must too.
    assert any(msg.startswith("Root Match:") for msg in legacy_messages)
    assert native_messages == legacy_messages


@requires_rust_parser
def test__parity__native_ast_parse_node_accounting_parity(monkeypatch):
    """Both build paths make identical parse-node accounting increments.

    The max_parse_nodes budget (a DoS guard) is charged as the BaseSegment
    tree is built - in MatchResult.apply on the legacy path and in
    _apply_rs_match_result on the fused path. Counting differently between
    the two paths would mean the same SQL with the same max_parse_nodes
    limit could parse under one flag and raise SQLParseError under the
    other. Confirms the final consumed budget matches, and that behaviour
    at the exact budget boundary (the smallest passing limit, and one below
    it) is identical - the boundary probe is driven purely through SQL plus
    config, the same way a user would hit it.
    """
    from sqlfluff.core.parser.context import ParseContext

    captured = []
    orig_from_config = ParseContext.from_config.__func__

    def _capturing_from_config(cls, config):
        ctx = orig_from_config(cls, config)
        captured.append(ctx)
        return ctx

    monkeypatch.setattr(
        ParseContext, "from_config", classmethod(_capturing_from_config)
    )

    sql = "SELECT a, b FROM t WHERE x = 1"

    captured.clear()
    _native_and_legacy(sql)
    # _native_and_legacy parses native-first: one context per parse.
    assert len(captured) == 2
    native_count, legacy_count = (ctx.current_parse_nodes for ctx in captured)
    assert native_count == legacy_count

    # Boundary behaviour: find the smallest max_parse_nodes that lets the
    # legacy path build the tree (the effective floor may be enforced by
    # either the shared Rust core or the Python-side ParseContext budget),
    # then require the native path to agree exactly both at that limit and
    # just below it (where both must raise the same SQLParseError).
    lo, hi = 1, 4000
    while lo < hi:
        mid = (lo + hi) // 2
        _, legacy_capture = _native_and_legacy(sql, configs={"max_parse_nodes": mid})
        if legacy_capture[0] == "tree":
            hi = mid
        else:
            lo = mid + 1
    for limit in (lo, lo - 1):
        native_capture, legacy_capture = _native_and_legacy(
            sql, configs={"max_parse_nodes": limit}
        )
        assert native_capture == legacy_capture
    # And the boundary is real: passing at the floor, SQLParseError below.
    assert _native_and_legacy(sql, configs={"max_parse_nodes": lo})[1][0] == "tree"
    below = _native_and_legacy(sql, configs={"max_parse_nodes": lo - 1})[1]
    assert below[0] == "exc" and below[1] == "SQLParseError"


@requires_rust_parser
@pytest.mark.xfail(
    strict=True,
    reason=(
        "Known gap: the max_parse_nodes budget is enforced twice with "
        "different counting semantics - the Rust core counts its internal "
        "match-tree nodes and raises before Python-side building, while the "
        "pure-Python parser counts materialized parse nodes. For the same "
        "SQL the minimal passing limit differs (e.g. 46 vs 50 for a simple "
        "SELECT), so limits in that window parse under one engine and raise "
        "SQLParseError under the other."
    ),
)
def test__parity__vs_python_max_parse_nodes_threshold():
    """The same max_parse_nodes limit should behave identically on both engines."""
    from sqlfluff.core.parser import Lexer

    sql = "SELECT a, b FROM t WHERE x = 1"

    def outcome(engine, limit):
        config = build_config(configs={"max_parse_nodes": limit})
        segments, _ = Lexer(config=config).lex(sql)
        return parse_capture(engine, config, segments)[:2]

    # Find Python's minimal passing limit, then require Rust to agree at
    # that limit and one below it.
    lo, hi = 1, 4000
    while lo < hi:
        mid = (lo + hi) // 2
        if outcome("python", mid)[0] == "tree":
            hi = mid
        else:
            lo = mid + 1
    assert outcome("rust", lo) == outcome("python", lo)
    assert outcome("rust", lo - 1) == outcome("python", lo - 1)


@requires_rust_parser
def test__parity__int_typed_indentation_config_stays_int():
    """The config layer stores bool-ish indentation values as int.

    The pinned parity case ``config_parity.yml:int_typed_indentation_config``
    exists because RustParser used to drop int-typed indentation settings
    and treat them as bool. This companion guard confirms the config layer
    still produces int typing, so that case keeps exercising what it was
    written for.
    """
    config = build_config()
    config.set_value(["indentation", "indented_joins"], True)
    stored = config.get_section("indentation")["indented_joins"]
    assert stored == 1 and not isinstance(stored, bool)


@pytest.mark.xfail(
    strict=True,
    reason=(
        "Known dialect gap: dialect_tsql.py's money-literal lexer pattern is "
        'built from \'"".join(sets("currency_symbols"))\' without sorted(), so '
        "the joined regex bytes depend on the interpreter's string-hash seed and "
        "differ across PYTHONHASHSEED values. Sorting that join (as the other "
        "tsql patterns already do) removes this xfail."
    ),
)
@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason=(
        "The Windows console encoding crashes the probe subprocess outright "
        "(before the real hash-seed mismatch can surface), so the strict xfail "
        "can't be relied on there. Skipped on Windows until the dialect fix lands."
    ),
)
def test__parity__codegen_lexer_patterns_hash_seed_stable():
    """Dialect lexer regexes stay identical across interpreter hash seeds.

    Regression test for the tsql money-literal lexer pattern, which was
    assembled from an unordered set of currency symbols: its bytes changed
    with the interpreter's hash seed, so the generated Rust lexer file
    (snapshotted by utils/rustify.py) reproduced inconsistently and the
    codegen freshness check failed spuriously. The full matcher list is
    compared, so this also catches any future set-ordered pattern in any
    tsql matcher.
    """
    import os
    import subprocess

    script = (
        "from sqlfluff.core.dialects import dialect_selector\n"
        "d = dialect_selector('tsql')\n"
        "for m in d.lexer_matchers:\n"
        "    print(m.name, repr(getattr(m, 'template', None)))\n"
    )
    outputs = set()
    for seed in ("0", "1", "2"):
        # Force UTF-8 for the child's stdout: some tsql lexer templates embed
        # non-ASCII currency symbols, and without this the child's print()
        # encodes to the platform's default codepage (e.g. cp1252 on
        # Windows), which can't represent them and crashes the subprocess for
        # a reason unrelated to hash-seed stability.
        env = dict(os.environ, PYTHONHASHSEED=seed, PYTHONIOENCODING="utf-8")
        proc = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True,
            env=env,
            check=True,
            timeout=120,
        )
        outputs.add(proc.stdout)
    assert len(outputs) == 1, "lexer matcher patterns vary with the hash seed"


@requires_rust_parser
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
def test__parity__tsql_datatype_method_case_sensitive(method, is_datatype_method):
    """Rust parser honors ``ignore_case=False``.

    ``col.value(...)`` is a data-type method (case-sensitive, lowercase only),
    while ``col.VALUE(...)`` and ``col.Value(...)`` are plain identifiers. The
    Rust parser should match Python here, so this test checks both the
    parity between them and the semantic direction itself.
    """
    from sqlfluff.core import FluffConfig, Linter

    src = f"SELECT col.{method}('/x', 'y') FROM t;\n"

    def method_ids(rust):
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
    python_ids = method_ids(False)
    assert rust_ids == python_ids
    assert (method in rust_ids) is is_datatype_method
