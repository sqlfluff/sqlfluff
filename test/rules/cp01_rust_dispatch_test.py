"""Dispatch tests for Rust-native CP01 via `core.use_rust_rules`.

These exercise the real linter path: with `use_rust_rules=True`, CP01's
`_eval_rust` runs the detection in Rust over the arena and the linter applies
the resulting fixes. The tests assert (a) the fixed SQL is identical to the
stock Python path, and (b) the Rust path is actually engaged when enabled (and
not when disabled).
"""

from unittest import mock

import pytest

from sqlfluff.core import FluffConfig, Linter
from sqlfluff.core.errors import SQLFluffUserError

try:
    import sqlfluffrs
    from sqlfluff.core.parser.rust_parser import _HAS_RUST_PARSER
except ImportError:  # pragma: no cover
    _HAS_RUST_PARSER = False


def _linter(policy, use_rust_rules, ignore_words=None):
    lines = [
        "[sqlfluff]",
        "dialect=ansi",
        "rules=CP01",
        "use_rust_parser=True",
        f"use_rust_rules={use_rust_rules}",
        "[sqlfluff:rules:capitalisation.keywords]",
        f"capitalisation_policy={policy}",
    ]
    if ignore_words:
        lines.append(f"ignore_words={ignore_words}")
    return Linter(config=FluffConfig.from_string("\n".join(lines) + "\n"))


def _fixed(policy, use_rust_rules, sql, ignore_words=None):
    res = _linter(policy, use_rust_rules, ignore_words).lint_string(sql, fix=True)
    return res.fix_string()[0]


_SAMPLES = [
    "select a, b FROM t WHERE x = 1 ORDER by a",
    "SELECT count(*) from foo group BY a having a > 1",
    "select CASE when a then 1 else 2 END as c from t",
    "select a + b, a > b, a AND b OR c from t",
    "create table t (a INT, b Varchar(10), c TIMESTAMP)",
    "select TRUE, false, NULL, a is not NULL from t",
    "SELECT A FROM B",
    "select a from b",
]


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
@pytest.mark.parametrize("policy", ["consistent", "upper", "lower", "capitalise"])
@pytest.mark.parametrize("sql", _SAMPLES)
def test__cp01_dispatch__fix_parity(policy, sql):
    """Fixing through the linter is identical with use_rust_rules on vs off."""
    assert _fixed(policy, "True", sql) == _fixed(policy, "False", sql)


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__cp01_dispatch__ignore_words_parity():
    """ignore_words is honoured identically on the Rust path."""
    sql = "select a from t where x = 1"
    assert _fixed("upper", "True", sql, ignore_words="from,where") == _fixed(
        "upper", "False", sql, ignore_words="from,where"
    )


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__cp01_dispatch__engages_rust_only_when_enabled():
    """The Rust detection is called when enabled, and not when disabled."""
    sql = "SeLeCt 1 FROM t"

    with mock.patch(
        "sqlfluffrs.cp01_violations", wraps=sqlfluffrs.cp01_violations
    ) as spy:
        _linter("consistent", "True").lint_string(sql, fix=True)
    assert spy.called, "expected the Rust detection to run when use_rust_rules=True"

    with mock.patch(
        "sqlfluffrs.cp01_violations", wraps=sqlfluffrs.cp01_violations
    ) as spy:
        _linter("consistent", "False").lint_string(sql, fix=True)
    assert not spy.called, "Rust detection must not run when use_rust_rules=False"


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__cp01_dispatch__regex_ignore_falls_back_to_python():
    """ignore_words_regex isn't implemented natively -> Python fallback, no call."""
    cfg = FluffConfig.from_string(
        "[sqlfluff]\ndialect=ansi\nrules=CP01\nuse_rust_parser=True\n"
        "use_rust_rules=True\n"
        "[sqlfluff:rules:capitalisation.keywords]\n"
        "capitalisation_policy=upper\nignore_words_regex=^x\n"
    )
    with mock.patch(
        "sqlfluffrs.cp01_violations", wraps=sqlfluffrs.cp01_violations
    ) as spy:
        Linter(config=cfg).lint_string("select a from t", fix=True)
    assert not spy.called, "regex word-ignore should fall back to the Python rule"


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__dispatch__rule_without_rust_path_falls_back():
    """A rule that doesn't override _eval_rust uses the base hook (None) -> Python.

    Exercises BaseRule._eval_rust's default and confirms an un-ported rule is
    unaffected by use_rust_rules.
    """

    def fixed(use_rust_rules):
        cfg = FluffConfig.from_string(
            "[sqlfluff]\ndialect=ansi\nrules=LT01\nuse_rust_parser=True\n"
            f"use_rust_rules={use_rust_rules}\n"
        )
        return Linter(config=cfg).lint_string("SELECT  1", fix=True).fix_string()[0]

    assert fixed("True") == fixed("False")


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__dispatch__cp03_inherits_eval_rust_and_falls_back():
    """CP03 inherits CP01._eval_rust but uses a different policy key.

    It must fall back to Python (not crash on a missing capitalisation_policy)
    and produce identical fixes with use_rust_rules on vs off.
    """

    def fixed(use_rust_rules):
        cfg = FluffConfig.from_string(
            "[sqlfluff]\ndialect=ansi\nrules=CP03\nuse_rust_parser=True\n"
            f"use_rust_rules={use_rust_rules}\n"
        )
        sql = "select MAX(x), Min(y) from t"
        return Linter(config=cfg).lint_string(sql, fix=True).fix_string()[0]

    assert fixed("True") == fixed("False")


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__dispatch__cp04_not_hijacked_by_cp01_rust_path():
    """CP04 (literals) shares capitalisation_policy but must NOT use CP01's path.

    CP01's Rust detection excludes literals; CP04 inheriting it unguarded would
    silently miss boolean/null literal violations. The name-guard prevents that,
    so CP04 fixes are identical with use_rust_rules on vs off.
    """

    def fixed(use_rust_rules):
        cfg = FluffConfig.from_string(
            "[sqlfluff]\ndialect=ansi\nrules=CP04\nuse_rust_parser=True\n"
            f"use_rust_rules={use_rust_rules}\n"
        )
        sql = "select true, FALSE, null from t"
        return Linter(config=cfg).lint_string(sql, fix=True).fix_string()[0]

    assert fixed("True") == fixed("False")


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__dispatch__rust_error_is_recoverable():
    """A Rust-side error surfaces as a violation, not a crash that aborts linting."""
    cfg = FluffConfig.from_string(
        "[sqlfluff]\ndialect=ansi\nrules=CP01\nuse_rust_parser=True\n"
        "use_rust_rules=True\n"
    )
    with mock.patch("sqlfluffrs.cp01_violations", side_effect=RuntimeError("boom")):
        result = Linter(config=cfg).lint_string("SeLeCt 1", fix=False)
    assert any("Unexpected exception" in v.description for v in result.violations)


def test__use_rust_rules_requires_rust_parser():
    """Enabling rust rules while disabling the rust parser is rejected."""
    # Contradiction: explicit rules-on + explicit parser-off.
    with pytest.raises(SQLFluffUserError, match="use_rust_parser"):
        FluffConfig.from_string(
            "[sqlfluff]\ndialect=ansi\nuse_rust_parser=False\nuse_rust_rules=True\n"
        )
    # auto degrades gracefully (not an error) even with the parser off.
    FluffConfig.from_string(
        "[sqlfluff]\ndialect=ansi\nuse_rust_parser=False\nuse_rust_rules=auto\n"
    )
    # The valid combinations construct fine.
    FluffConfig.from_string(
        "[sqlfluff]\ndialect=ansi\nuse_rust_parser=auto\nuse_rust_rules=True\n"
    )
