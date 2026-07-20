"""Dispatch tests for Rust-native CP04 via `core.use_rust_rules`.

These exercise the real linter path: with `use_rust_rules=True`, CP04's
`_eval_rust` runs the detection in Rust over the arena and the linter applies
the resulting fixes. The tests assert (a) the fixed SQL is identical to the
stock Python path, and (b) the Rust path is actually engaged when enabled (and
not when disabled) — and specifically that CP04 does NOT get hijacked by
CP01's inherited path (they share `capitalisation_policy`).
"""

from unittest import mock

import pytest

from sqlfluff.core import FluffConfig, Linter

try:
    import sqlfluffrs
    from sqlfluff.core.parser.rust_parser import _HAS_RUST_PARSER
except ImportError:  # pragma: no cover
    _HAS_RUST_PARSER = False


def _linter(policy, use_rust_rules, ignore_words=None):
    lines = [
        "[sqlfluff]",
        "dialect=ansi",
        "rules=CP04",
        "use_rust_parser=True",
        f"use_rust_rules={use_rust_rules}",
        "[sqlfluff:rules:capitalisation.literals]",
        f"capitalisation_policy={policy}",
    ]
    if ignore_words:
        lines.append(f"ignore_words={ignore_words}")
    return Linter(config=FluffConfig.from_string("\n".join(lines) + "\n"))


def _fixed(policy, use_rust_rules, sql, ignore_words=None):
    res = _linter(policy, use_rust_rules, ignore_words).lint_string(sql, fix=True)
    return res.fix_string()[0]


_SAMPLES = [
    "select TRUE, false, NULL, a is not NULL from t",
    "select true, FALSE, null from t",
    "select a, TRUE from t where b = FALSE",
    "select NULL from t",
    "select true from t",
]


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
@pytest.mark.parametrize("policy", ["consistent", "upper", "lower", "capitalise"])
@pytest.mark.parametrize("sql", _SAMPLES)
def test__cp04_dispatch__fix_parity(policy, sql):
    """Fixing through the linter is identical with use_rust_rules on vs off."""
    assert _fixed(policy, "True", sql) == _fixed(policy, "False", sql)


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__cp04_dispatch__ignore_words_parity():
    """ignore_words is honoured identically on the Rust path."""
    sql = "select true, false from t"
    assert _fixed("upper", "True", sql, ignore_words="true") == _fixed(
        "upper", "False", sql, ignore_words="true"
    )


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__cp04_dispatch__engages_rust_only_when_enabled():
    """The Rust detection is called when enabled, and not when disabled."""
    sql = "select TrUe, FaLsE from t"

    with mock.patch(
        "sqlfluffrs.cp04_violations", wraps=sqlfluffrs.cp04_violations
    ) as spy:
        _linter("consistent", "True").lint_string(sql, fix=True)
    assert spy.called, "expected the Rust detection to run when use_rust_rules=True"

    with mock.patch(
        "sqlfluffrs.cp04_violations", wraps=sqlfluffrs.cp04_violations
    ) as spy:
        _linter("consistent", "False").lint_string(sql, fix=True)
    assert not spy.called, "Rust detection must not run when use_rust_rules=False"


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__cp04_dispatch__regex_ignore_falls_back_to_python():
    """ignore_words_regex isn't implemented natively -> Python fallback, no call."""
    cfg = FluffConfig.from_string(
        "[sqlfluff]\ndialect=ansi\nrules=CP04\nuse_rust_parser=True\n"
        "use_rust_rules=True\n"
        "[sqlfluff:rules:capitalisation.literals]\n"
        "capitalisation_policy=upper\nignore_words_regex=^x\n"
    )
    with mock.patch(
        "sqlfluffrs.cp04_violations", wraps=sqlfluffrs.cp04_violations
    ) as spy:
        Linter(config=cfg).lint_string("select true from t", fix=True)
    assert not spy.called, "regex word-ignore should fall back to the Python rule"


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__cp04_dispatch__not_hijacked_by_cp01_rust_path():
    """CP04 shares capitalisation_policy with CP01 but must use its own path.

    CP01's Rust detection excludes literals; an unguarded shared dispatch would
    silently miss boolean/null literal violations here.
    """
    with (
        mock.patch(
            "sqlfluffrs.cp01_violations", wraps=sqlfluffrs.cp01_violations
        ) as cp01_spy,
        mock.patch(
            "sqlfluffrs.cp04_violations", wraps=sqlfluffrs.cp04_violations
        ) as cp04_spy,
    ):
        _linter("consistent", "True").lint_string(
            "select true, FALSE, null from t", fix=True
        )
    assert cp04_spy.called
    assert not cp01_spy.called
