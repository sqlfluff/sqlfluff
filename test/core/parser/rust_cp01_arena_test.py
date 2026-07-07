"""Parity tests for the experimental Rust-native CP01 detection over the arena.

PROTOTYPE: `sqlfluffrs.cp01_violations(tree, ...)` runs CP01's detection loop
entirely in Rust (in the `sqlfluffrs_rules` crate, over the arena read API) and
returns `(leaf_index, fixed_raw)` pairs. It is NOT wired into rule dispatch —
these tests exercise the function directly and assert it produces the same fixes
as the stock Python `Rule_CP01`. Anchoring is by leaf index (1:1 with
`raw_segments`); arena and Python uuids are not shared.
"""

import pytest

from sqlfluff.core import FluffConfig, Linter

try:
    import sqlfluffrs
    from sqlfluff.core.parser.rust_parser import _HAS_RUST_PARSER
except ImportError:  # pragma: no cover
    _HAS_RUST_PARSER = False


def _cfg(policy="consistent"):
    """Config that genuinely sets CP01's policy (overrides don't reach rules)."""
    return FluffConfig.from_string(
        "[sqlfluff]\ndialect=ansi\nrules=CP01\nuse_rust_parser=True\n"
        "[sqlfluff:rules:capitalisation.keywords]\n"
        f"capitalisation_policy={policy}\n"
    )


# SQL exercising selection + CP01's exclusion branches: plain keywords, binary
# operators, CASE, data-type parents, keyword-literals, UDF function_name,
# already-correct, and mixed casing.
_SAMPLES = [
    "select a, b FROM t WHERE x = 1 ORDER by a",
    "SELECT count(*) from foo group BY a having a > 1",
    "select CASE when a then 1 else 2 END as c from t",
    "select a + b, a > b, a AND b OR c from t",
    "create table t (a INT, b Varchar(10), c TIMESTAMP)",
    "select my_schema.my_udf(a), Count(b) from t",
    "select TRUE, false, NULL, a is not NULL from t",
    "SELECT A FROM B",
    "select a from b",
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
    rule = next(r for r in linter.get_rulepack(cfg).rules if r.code == "CP01")
    policy = str(getattr(rule, "capitalisation_policy", "consistent"))
    by_idx = dict(sqlfluffrs.cp01_violations(tree._rs_tree, policy, [], False))
    return "".join(by_idx.get(i, seg.raw) for i, seg in enumerate(tree.raw_segments))


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
@pytest.mark.parametrize("policy", ["consistent", "upper", "lower", "capitalise"])
@pytest.mark.parametrize("sql", _SAMPLES)
def test__cp01_arena__matches_stock(policy, sql):
    """Arena-native CP01 detection produces identical fixes to stock CP01."""
    cfg = _cfg(policy)
    linter = Linter(config=cfg)
    assert _arena_fixed(linter, cfg, sql) == _stock_fixed(linter, sql)


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__cp01_arena__leaf_index_aligns_with_raw_segments():
    """The arena's leaf order is 1:1 with Python raw_segments (anchor contract)."""
    cfg = _cfg("upper")
    tree = Linter(config=cfg).parse_string("select a from t").tree
    arena_leaves = tree._rs_tree.root.raw_segments()
    assert len(arena_leaves) == len(tree.raw_segments)
    for leaf, seg in zip(arena_leaves, tree.raw_segments):
        assert leaf.raw == seg.raw


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__cp01_arena__honours_ignore_words():
    """An ignored keyword is left untouched by the native detection."""
    cfg = _cfg("upper")
    tree = Linter(config=cfg).parse_string("select a from t").tree
    # Ignore "from": only "select" should be flagged for upper-casing.
    fixed_raws = {
        fixed
        for _, fixed in sqlfluffrs.cp01_violations(
            tree._rs_tree, "upper", ["from"], False
        )
    }
    assert "SELECT" in fixed_raws
    assert "FROM" not in fixed_raws
