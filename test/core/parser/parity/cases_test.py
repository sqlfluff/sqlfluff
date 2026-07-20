"""Drivers for the parity case corpus in ``test/fixtures/parity/``.

Each YAML case is just data: SQL (inline or from a dialect-corpus fixture),
dialect, config and metadata. ``compare.py`` holds the shared capture and
comparison logic that every driver uses, so every case is checked at the
same strict level. Known differences are recorded in the fixture as a
strict xfail for the specific leg they affect (python_vs_rust or
native_vs_legacy).
"""

import pytest

from .compare import (
    PARSER_LEGS,
    build_config,
    check_expectations,
    lex_capture,
    linted_parse_capture,
    load_case_params,
    load_reference_case_params,
    parse_capture,
    raw_match_violations,
    reference_capture,
    requires_rust_parser,
    resolve_case_sql,
)


@pytest.mark.parametrize("case", load_reference_case_params("parser"))
def test__parity__parser_case_reference_expectations(case):
    """Confirm the Python parser still behaves as this case's ``expect`` claims.

    This is a regression guard on the pinned case itself, not an engine
    comparison: it catches the Python parser's behavior changing on this SQL
    (or ``expect`` having been wrong all along). It runs as its own test, so
    it still catches that even when the case is marked as a known engine
    divergence (xfail) in the comparison test below.
    """
    check_expectations(case, reference_capture(case))


@requires_rust_parser
@pytest.mark.parametrize("case,leg", load_case_params("parser", legs=list(PARSER_LEGS)))
def test__parity__parser_case(case, leg):
    """Confirm both engines of the leg produce identical parse results."""
    sql = resolve_case_sql(case)

    if case.get("templater"):
        # Templated cases go through linted_parse_capture, which builds its own
        # config; don't build one here (it would be discarded).
        left_engine, right_engine = PARSER_LEGS[leg]
        left = linted_parse_capture(
            left_engine,
            sql,
            dialect=case.get("dialect", "ansi"),
            configs=case.get("configs"),
            context=case.get("context"),
        )
        right = linted_parse_capture(
            right_engine,
            sql,
            dialect=case.get("dialect", "ansi"),
            configs=case.get("configs"),
            context=case.get("context"),
        )
        assert left == right
        return

    from sqlfluff.core.parser import Lexer

    config = build_config(case.get("dialect", "ansi"), case.get("configs"))
    # Both engines parse the SAME lexed segments: this isolates parser
    # parity from lexer parity (which has its own leg).
    segments, _ = Lexer(config=config).lex(sql)
    left_engine, right_engine = PARSER_LEGS[leg]
    left = parse_capture(left_engine, config, segments)
    right = parse_capture(right_engine, config, segments)
    assert left == right


@requires_rust_parser
@pytest.mark.parametrize("case,leg", load_case_params("lexer", legs=["lexer"]))
def test__parity__lexer_case(case, leg):
    """Confirm PyRsLexer's token stream and errors match PyLexer's exactly."""
    sql = resolve_case_sql(case)
    config = build_config(case.get("dialect", "ansi"), case.get("configs"))
    assert lex_capture("rust", config, sql) == lex_capture("python", config, sql)


@requires_rust_parser
@pytest.mark.parametrize(
    "case,leg", load_case_params("invariants", legs=["invariants"])
)
def test__parity__match_result_invariants(case, leg):
    """Confirm the returned RsMatchResults, as in the internal tree, are structurally well-formed."""
    sql = resolve_case_sql(case)
    assert raw_match_violations(sql, case.get("dialect", "ansi")) == []
