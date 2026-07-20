"""Three-way parity sweep over the whole dialect fixture corpus.

For every ``test/fixtures/dialects/**/*.sql`` fixture, parse the same lexer
output three ways - the pure-Python Parser, RustParser's legacy convert+apply
path, and RustParser's fused native-AST builder - and assert all three results
are identical at full strictness.

Parity must hold for every dialect since the engine flags affect all of them;
covering the whole corpus also exercises the rarer builder branches (e.g.
zero-length matches).
"""

import pytest

from .compare import (
    DIALECT_FIXTURE_DIR,
    build_config,
    parse_capture,
    requires_rust_parser,
)

_FIXTURE_SQL = sorted(DIALECT_FIXTURE_DIR.glob("*/*.sql"))

# Fixtures with a *known*, already-documented Python-vs-RustParser divergence
# (pin each with a dedicated case in test/fixtures/parity/ before listing it
# here). Three-way parity below is expected to fail on exactly these until
# those bugs are fixed; everywhere else in the corpus, all three tree-building
# paths must agree.
_KNOWN_PYTHON_RUST_DIVERGENCES: set = {
    # All of the fixtures below hit the same bug: RustParser forwards a
    # re-wrapped token's lexer-level trim_chars (e.g. the '@'/'@@'
    # sigil trimmed off MySQL/MariaDB/BigQuery session-variable and parameter
    # tokens) into the new segment's kwargs, where Python's
    # RawSegment.from_result_segments only ever carries over
    # quoted_value/escape_replacements/casefold, never trim_chars. See the
    # pinned case parser_created_segments_drop_token_trim_chars in
    # test/fixtures/parity/regressions.yml.
    ("bigquery", "handle_exception.sql"),
    ("bigquery", "parameters.sql"),
    ("bigquery", "set_variable_single.sql"),
    ("mariadb", "call_statement.sql"),
    ("mariadb", "create_trigger.sql"),
    ("mariadb", "create_user.sql"),
    ("mariadb", "execute_prepared_stmt_using.sql"),
    ("mariadb", "execute_prepared_stmt_using_multiple_variable.sql"),
    ("mariadb", "fetch_session.sql"),
    ("mariadb", "fetch_session_multiple.sql"),
    ("mariadb", "function_definer.sql"),
    ("mariadb", "get_diagnostics_condition_info_multiple_variable.sql"),
    ("mariadb", "get_diagnostics_condition_info_session_variable.sql"),
    ("mariadb", "get_diagnostics_condition_session_variable.sql"),
    ("mariadb", "get_diagnostics_number.sql"),
    ("mariadb", "get_diagnostics_row_count.sql"),
    ("mariadb", "grant.sql"),
    ("mariadb", "if.sql"),
    ("mariadb", "if_else.sql"),
    ("mariadb", "if_elseif.sql"),
    ("mariadb", "if_multiple_expression.sql"),
    ("mariadb", "if_nested.sql"),
    ("mariadb", "if_session_variable.sql"),
    ("mariadb", "if_subquery_expression.sql"),
    ("mariadb", "json_table.sql"),
    ("mariadb", "load_data.sql"),
    ("mariadb", "nested_begin.sql"),
    ("mariadb", "prepare_session_variable.sql"),
    ("mariadb", "procedure_definer.sql"),
    ("mariadb", "repeat_label.sql"),
    ("mariadb", "repeat_multiple_statements.sql"),
    ("mariadb", "repeat_no_label.sql"),
    ("mariadb", "select_into_multiple_variable.sql"),
    ("mariadb", "select_into_session_variable.sql"),
    ("mariadb", "select_session_variable.sql"),
    ("mariadb", "set.sql"),
    ("mariadb", "system_variables.sql"),
    ("mariadb", "variable_assignment.sql"),
    ("mysql", "call_statement.sql"),
    ("mysql", "create_trigger.sql"),
    ("mysql", "create_user.sql"),
    ("mysql", "execute_prepared_stmt_using.sql"),
    ("mysql", "execute_prepared_stmt_using_multiple_variable.sql"),
    ("mysql", "fetch_session.sql"),
    ("mysql", "fetch_session_multiple.sql"),
    ("mysql", "function_definer.sql"),
    ("mysql", "get_diagnostics_condition_info_multiple_variable.sql"),
    ("mysql", "get_diagnostics_condition_info_session_variable.sql"),
    ("mysql", "get_diagnostics_condition_session_variable.sql"),
    ("mysql", "get_diagnostics_number.sql"),
    ("mysql", "get_diagnostics_row_count.sql"),
    ("mysql", "grant.sql"),
    ("mysql", "if.sql"),
    ("mysql", "if_else.sql"),
    ("mysql", "if_elseif.sql"),
    ("mysql", "if_multiple_expression.sql"),
    ("mysql", "if_nested.sql"),
    ("mysql", "if_session_variable.sql"),
    ("mysql", "if_subquery_expression.sql"),
    ("mysql", "json_table.sql"),
    ("mysql", "load_data.sql"),
    ("mysql", "nested_begin.sql"),
    ("mysql", "prepare_session_variable.sql"),
    ("mysql", "procedure_definer.sql"),
    ("mysql", "repeat_label.sql"),
    ("mysql", "repeat_multiple_statements.sql"),
    ("mysql", "repeat_no_label.sql"),
    ("mysql", "select_into_multiple_variable.sql"),
    ("mysql", "select_into_session_variable.sql"),
    ("mysql", "select_session_variable.sql"),
    ("mysql", "set.sql"),
    ("mysql", "system_variables.sql"),
    ("mysql", "variable_assignment.sql"),
}


_KNOWN_DIVERGENCE_REASON = (
    "Known Python-vs-RustParser divergence on this fixture; "
    "see the pinned case in test/fixtures/parity/."
)


@requires_rust_parser
@pytest.mark.parametrize(
    "sqlfile",
    _FIXTURE_SQL,
    ids=[str(p.relative_to(DIALECT_FIXTURE_DIR)) for p in _FIXTURE_SQL],
)
def test__parity__dialect_fixture_corpus(sqlfile):
    """All three tree-building paths agree on this fixture."""
    from sqlfluff.core.parser import Lexer

    config = build_config(dialect=sqlfile.parent.name)
    segments, _ = Lexer(config=config).lex(sqlfile.read_text(encoding="utf-8"))

    python_capture = parse_capture("python", config, segments, fname=str(sqlfile))
    rust_capture = parse_capture("rust", config, segments, fname=str(sqlfile))
    native_capture = parse_capture("rust-native", config, segments, fname=str(sqlfile))

    # Native-vs-legacy parity is never a "known divergence": a failure here is
    # always a bug in one of RustParser's two build paths, so it must never be
    # silently swallowed by a python-vs-rust xfail below.
    assert native_capture == rust_capture, "native-AST path diverges from convert+apply"

    is_known = (sqlfile.parent.name, sqlfile.name) in _KNOWN_PYTHON_RUST_DIVERGENCES
    matches = python_capture == rust_capture
    if is_known:
        if matches:
            pytest.fail(
                f"{sqlfile}: no longer diverges; remove this fixture from "
                "_KNOWN_PYTHON_RUST_DIVERGENCES"
            )
        pytest.xfail(_KNOWN_DIVERGENCE_REASON)
    assert matches, "RustParser diverges from Python Parser"
