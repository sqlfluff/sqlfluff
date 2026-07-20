"""Parity tests for the experimental Rust-native CP03 detection over the arena.

`sqlfluffrs.cp03_violations(tree, ...)` runs CP03's (function-name
capitalisation) detection loop entirely in Rust, over the shared
`sqlfluffrs_rules::capitalisation` state machine, and returns
`(leaf_index, fixed_raw)` pairs. These tests exercise the function directly and
assert it produces the same fixes as the stock Python `Rule_CP03`, across the
extended policy set (`pascal`/`camel`/`snake` in addition to CP01's four).
Anchoring is by leaf index (1:1 with `raw_segments`); arena and Python uuids
are not shared.
"""

import pytest

from sqlfluff.core import FluffConfig, Linter

try:
    import sqlfluffrs
    from sqlfluff.core.parser.rust_parser import _HAS_RUST_PARSER
except ImportError:  # pragma: no cover
    _HAS_RUST_PARSER = False


def _cfg(policy="consistent"):
    """Config that genuinely sets CP03's policy (overrides don't reach rules)."""
    return FluffConfig.from_string(
        "[sqlfluff]\ndialect=ansi\nrules=CP03\nuse_rust_parser=True\n"
        "[sqlfluff:rules:capitalisation.functions]\n"
        f"extended_capitalisation_policy={policy}\n"
    )


# SQL exercising function-name targets, including a qualified (UDF-like,
# case-sensitive) name that must be excluded, bare functions, mixed casing,
# and multi-word names for the pascal/camel/snake transforms.
_SAMPLES = [
    "select sum(a) as aa, SUM(b) as bb from foo",
    "select my_schema.my_udf(a), Count(b) from t",
    "select current_timestamp, CURRENT_USER from t",
    "select MyFunc(a), other_func(b) from t",
    "SELECT COUNT(*) FROM t",
    "select count(*) from t",
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
    rule = next(r for r in linter.get_rulepack(cfg).rules if r.code == "CP03")
    policy = str(getattr(rule, "extended_capitalisation_policy", "consistent"))
    by_idx = dict(sqlfluffrs.cp03_violations(tree._rs_tree, policy, [], False))
    return "".join(by_idx.get(i, seg.raw) for i, seg in enumerate(tree.raw_segments))


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
@pytest.mark.parametrize(
    "policy", ["consistent", "upper", "lower", "capitalise", "pascal", "camel", "snake"]
)
@pytest.mark.parametrize("sql", _SAMPLES)
def test__cp03_arena__matches_stock(policy, sql):
    """Arena-native CP03 detection produces identical fixes to stock CP03."""
    cfg = _cfg(policy)
    linter = Linter(config=cfg)
    assert _arena_fixed(linter, cfg, sql) == _stock_fixed(linter, sql)


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__cp03_arena__excludes_qualified_function_name():
    """A multi-part (UDF-like) function name is left untouched."""
    cfg = _cfg("upper")
    tree = Linter(config=cfg).parse_string("select my_schema.my_udf(a) from t").tree
    by_idx = dict(sqlfluffrs.cp03_violations(tree._rs_tree, "upper", [], False))
    assert not by_idx


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__cp03_arena__honours_ignore_words():
    """An ignored function name is left untouched by the native detection."""
    cfg = _cfg("upper")
    tree = Linter(config=cfg).parse_string("select sum(a), count(b) from t").tree
    fixed_raws = {
        fixed
        for _, fixed in sqlfluffrs.cp03_violations(
            tree._rs_tree, "upper", ["sum"], False
        )
    }
    assert "COUNT" in fixed_raws
    assert "SUM" not in fixed_raws
