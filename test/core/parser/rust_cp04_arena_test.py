"""Parity tests for the experimental Rust-native CP04 detection over the arena.

`sqlfluffrs.cp04_violations(tree, ...)` runs CP04's (boolean/null literal
capitalisation) detection loop entirely in Rust, over the shared
`sqlfluffrs_rules::capitalisation` state machine, and returns
`(leaf_index, fixed_raw)` pairs. These tests exercise the function directly and
assert it produces the same fixes as the stock Python `Rule_CP04`. Anchoring is
by leaf index (1:1 with `raw_segments`); arena and Python uuids are not shared.
"""

import pytest

from sqlfluff.core import FluffConfig, Linter

try:
    import sqlfluffrs
    from sqlfluff.core.parser.rust_parser import _HAS_RUST_PARSER
except ImportError:  # pragma: no cover
    _HAS_RUST_PARSER = False


def _cfg(policy="consistent"):
    """Config that genuinely sets CP04's policy (overrides don't reach rules)."""
    return FluffConfig.from_string(
        "[sqlfluff]\ndialect=ansi\nrules=CP04\nuse_rust_parser=True\n"
        "[sqlfluff:rules:capitalisation.literals]\n"
        f"capitalisation_policy={policy}\n"
    )


_SAMPLES = [
    "select TRUE, false, NULL, a is not NULL from t",
    "select true, FALSE, null from t",
    "select a, TRUE from t where b = FALSE",
    "select NULL from t",
    "select true from t",
]


def _stock_fixed(linter, sql):
    res = linter.lint_string(sql, fix=True)
    fixed, _ = res.fix_string()
    return fixed


def _arena_fixed(linter, cfg, sql):
    """Apply the Rust arena detection's fixes by leaf index, return fixed SQL."""
    tree = linter.parse_string(sql).tree
    if tree is None or getattr(tree, "_rs_tree", None) is None:
        return None
    rule = next(r for r in linter.get_rulepack(cfg).rules if r.code == "CP04")
    policy = str(getattr(rule, "capitalisation_policy", "consistent"))
    by_idx = dict(sqlfluffrs.cp04_violations(tree._rs_tree, policy, [], False))
    return "".join(by_idx.get(i, seg.raw) for i, seg in enumerate(tree.raw_segments))


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
@pytest.mark.parametrize("policy", ["consistent", "upper", "lower", "capitalise"])
@pytest.mark.parametrize("sql", _SAMPLES)
def test__cp04_arena__matches_stock(policy, sql):
    """Arena-native CP04 detection produces identical fixes to stock CP04."""
    cfg = _cfg(policy)
    linter = Linter(config=cfg)
    assert _arena_fixed(linter, cfg, sql) == _stock_fixed(linter, sql)


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__cp04_arena__honours_ignore_words():
    """An ignored literal is left untouched by the native detection."""
    cfg = _cfg("upper")
    tree = Linter(config=cfg).parse_string("select true, false from t").tree
    fixed_raws = {
        fixed
        for _, fixed in sqlfluffrs.cp04_violations(
            tree._rs_tree, "upper", ["true"], False
        )
    }
    assert "FALSE" in fixed_raws
    assert "TRUE" not in fixed_raws
