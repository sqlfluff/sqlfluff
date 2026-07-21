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
_KNOWN_PYTHON_RUST_DIVERGENCES: set = set()


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
