"""Dispatch tests for Rust-native CP03 via `core.use_rust_rules`.

These exercise the real linter path: with `use_rust_rules=True`, CP03's
`_eval_rust` runs the detection in Rust over the arena and the linter applies
the resulting fixes. The tests assert (a) the fixed SQL is identical to the
stock Python path, and (b) the Rust path is actually engaged when enabled (and
not when disabled).
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
        "rules=CP03",
        "use_rust_parser=True",
        f"use_rust_rules={use_rust_rules}",
        "[sqlfluff:rules:capitalisation.functions]",
        f"extended_capitalisation_policy={policy}",
    ]
    if ignore_words:
        lines.append(f"ignore_words={ignore_words}")
    return Linter(config=FluffConfig.from_string("\n".join(lines) + "\n"))


def _fixed(policy, use_rust_rules, sql, ignore_words=None):
    res = _linter(policy, use_rust_rules, ignore_words).lint_string(sql, fix=True)
    return res.fix_string()[0]


_SAMPLES = [
    "select sum(a) as aa, SUM(b) as bb from foo",
    "select my_schema.my_udf(a), Count(b) from t",
    "select MyFunc(a), other_func(b) from t",
    "SELECT COUNT(*) FROM t",
    "select count(*) from t",
]


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
@pytest.mark.parametrize(
    "policy", ["consistent", "upper", "lower", "capitalise", "pascal", "camel", "snake"]
)
@pytest.mark.parametrize("sql", _SAMPLES)
def test__cp03_dispatch__fix_parity(policy, sql):
    """Fixing through the linter is identical with use_rust_rules on vs off."""
    assert _fixed(policy, "True", sql) == _fixed(policy, "False", sql)


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__cp03_dispatch__ignore_words_parity():
    """ignore_words is honoured identically on the Rust path."""
    sql = "select sum(a), count(b) from t"
    assert _fixed("upper", "True", sql, ignore_words="sum") == _fixed(
        "upper", "False", sql, ignore_words="sum"
    )


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__cp03_dispatch__engages_rust_only_when_enabled():
    """The Rust detection is called when enabled, and not when disabled."""
    sql = "select SuM(a), MIN(b) from t"

    with mock.patch(
        "sqlfluffrs.cp03_violations", wraps=sqlfluffrs.cp03_violations
    ) as spy:
        _linter("consistent", "True").lint_string(sql, fix=True)
    assert spy.called, "expected the Rust detection to run when use_rust_rules=True"

    with mock.patch(
        "sqlfluffrs.cp03_violations", wraps=sqlfluffrs.cp03_violations
    ) as spy:
        _linter("consistent", "False").lint_string(sql, fix=True)
    assert not spy.called, "Rust detection must not run when use_rust_rules=False"


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__cp03_dispatch__regex_ignore_falls_back_to_python():
    """ignore_words_regex isn't implemented natively -> Python fallback, no call."""
    cfg = FluffConfig.from_string(
        "[sqlfluff]\ndialect=ansi\nrules=CP03\nuse_rust_parser=True\n"
        "use_rust_rules=True\n"
        "[sqlfluff:rules:capitalisation.functions]\n"
        "extended_capitalisation_policy=upper\nignore_words_regex=^x\n"
    )
    with mock.patch(
        "sqlfluffrs.cp03_violations", wraps=sqlfluffrs.cp03_violations
    ) as spy:
        Linter(config=cfg).lint_string("select sum(a) from t", fix=True)
    assert not spy.called, "regex word-ignore should fall back to the Python rule"


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__cp03_dispatch__not_hijacked_by_cp01_rust_path():
    """CP03's own _eval_rust must engage, not CP01's inherited one.

    CP03 uses extended_capitalisation_policy, which CP01's path doesn't read;
    an unguarded shared dispatch would either crash or silently no-op.
    """
    with (
        mock.patch(
            "sqlfluffrs.cp01_violations", wraps=sqlfluffrs.cp01_violations
        ) as cp01_spy,
        mock.patch(
            "sqlfluffrs.cp03_violations", wraps=sqlfluffrs.cp03_violations
        ) as cp03_spy,
    ):
        _linter("consistent", "True").lint_string(
            "select sum(a), MAX(b) from t", fix=True
        )
    assert cp03_spy.called
    assert not cp01_spy.called
