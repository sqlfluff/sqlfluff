"""Parity tests for the experimental Rust-assisted CP01 target selection.

These assert that picking CP01's targets by walking the Rust node tree
(_rs_cp01.cp01_results_via_rs_node) produces exactly the same fixes as stock
CP01, across the capitalisation policies and the rule's exclusion cases.
"""

import pytest

from sqlfluff.core import FluffConfig, Linter
from sqlfluff.core.rules import RuleContext

try:
    from sqlfluff.core.parser.rust_parser import _HAS_RUST_PARSER
    from sqlfluff.rules.capitalisation._rs_cp01 import (
        cp01_results_via_rs_node,
        cp01_targets_via_rs_node,
    )
except ImportError:  # pragma: no cover
    _HAS_RUST_PARSER = False


# SQL snippets chosen to exercise CP01's selection + every exclusion branch:
# plain keywords, binary operators, date_part, qualified UDF (function_name),
# data-type parents, keyword-literals (TRUE/NULL), already-correct, and mixed.
_SAMPLES = [
    "select a, b FROM t WHERE x = 1 ORDER by a",
    "SELECT count(*) from foo group BY a having a > 1",
    "select CASE when a then 1 else 2 END as c from t",
    "select a + b, a > b, a AND b OR c from t",
    "create table t (a INT, b Varchar(10), c TIMESTAMP)",
    "select date_part('year', d), extract(MONTH from d) from t",
    "select my_schema.my_udf(a), Count(b) from t",
    "select TRUE, false, NULL, a is not NULL from t",
    "SELECT A FROM B",
    "select a from b",
]


def _stock_fixed(linter, sql):
    res = linter.lint_string(sql, fix=True)
    fixed, _ = res.fix_string()
    return fixed


def _rs_fixed(linter, cfg, sql):
    parsed = linter.parse_string(sql)
    tree = parsed.tree
    if tree is None or getattr(tree, "_rs_node", None) is None:
        return None
    rule = next(r for r in linter.get_rulepack(cfg).rules if r.code == "CP01")
    ctx = RuleContext(
        dialect=cfg.get("dialect_obj"),
        fix=True,
        templated_file=None,
        path=None,
        config=cfg,
        segment=tree,
    )
    results = cp01_results_via_rs_node(rule, tree, ctx)
    replacements = {}
    for result in results:
        for fix in result.fixes or []:
            if fix.edit:
                replacements[id(fix.anchor)] = fix.edit[0].raw
    return "".join(replacements.get(id(s), s.raw) for s in tree.raw_segments)


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
@pytest.mark.parametrize("policy", ["consistent", "upper", "lower", "capitalise"])
@pytest.mark.parametrize("sql", _SAMPLES)
def test__cp01_rs_assist__matches_stock(policy, sql):
    """Rust-assisted CP01 produces identical fixes to stock CP01."""
    cfg = FluffConfig(
        overrides={
            "dialect": "ansi",
            "rules": "CP01",
            "use_rust_parser": True,
            "capitalisation_policy": policy,
        }
    )
    linter = Linter(config=cfg)
    assert _rs_fixed(linter, cfg, sql) == _stock_fixed(linter, sql)


@pytest.mark.skipif(not _HAS_RUST_PARSER, reason="Rust parser not available")
def test__cp01_rs_assist__falls_back_without_rs_node():
    """Selection returns None when no Rust node tree is attached."""
    cfg = FluffConfig(overrides={"dialect": "ansi", "use_rust_parser": True})
    linter = Linter(config=cfg)
    tree = linter.parse_string("select 1").tree
    assert tree is not None
    tree._rs_node = None
    assert cp01_targets_via_rs_node(tree) is None

    # The results helper falls back the same way.
    rule = next(r for r in linter.get_rulepack(cfg).rules if r.code == "CP01")
    ctx = RuleContext(
        dialect=cfg.get("dialect_obj"),
        fix=True,
        templated_file=None,
        path=None,
        config=cfg,
        segment=tree,
    )
    assert cp01_results_via_rs_node(rule, tree, ctx) is None
