"""Parity tests for the experimental RsSegment arena-façade lint/fix path.

For every rule in :data:`FACADE_SAFE_RULES`, run the façade's multi-pass
source-patch fix loop over each of that rule's ``std_rule_cases`` fixtures and
assert the fixed output matches the fixture's expected ``fix_str`` (or the input
unchanged for ``pass_str`` cases). Skipped unless the ``sqlfluffrs`` extension
provides ``engine_parse_to_tree``.
"""

import glob

import pytest
import yaml

try:
    import sqlfluffrs

    _HAS_ENGINE = hasattr(sqlfluffrs, "engine_parse_to_tree")
except ImportError:  # pragma: no cover
    _HAS_ENGINE = False

from sqlfluff.core import Linter
from sqlfluff.core.rules.rs_lint import FACADE_SAFE_RULES, facade_fix_loop
from sqlfluff.utils.testing.rules import _setup_config, load_test_cases

_CASE_DIR = "test/fixtures/rules/std_rule_cases"


def _facade_safe_cases():
    """Collect (id, test_case) for every case of a façade-safe rule."""
    collected = []
    for yaml_path in sorted(glob.glob(f"{_CASE_DIR}/*.yml")):
        with open(yaml_path) as f:
            doc = yaml.safe_load(f)
        if not doc or doc.get("rule") not in FACADE_SAFE_RULES:
            continue
        ids, cases = load_test_cases(yaml_path)
        for cid, tc in zip(ids, cases):
            src = tc.fail_str if tc.fail_str is not None else tc.pass_str
            if isinstance(src, str):
                collected.append(pytest.param(tc, id=cid))
    return collected


@pytest.mark.skipif(
    not _HAS_ENGINE, reason="sqlfluffrs.engine_parse_to_tree unavailable"
)
@pytest.mark.parametrize("test_case", _facade_safe_cases())
def test_facade_fix_matches_native(test_case) -> None:
    """Façade multi-pass fix output equals the fixture's expected result."""
    src = test_case.fail_str if test_case.fail_str is not None else test_case.pass_str
    config = _setup_config(test_case.rule, test_case.configs)
    linter = Linter(config=config)
    rules = list(linter.get_rulepack(config=config).rules)
    limit = int(config.get("runaway_limit"))

    fixed = facade_fix_loop(src, "<test>", config, rules, limit)
    expected = test_case.fix_str if test_case.fix_str is not None else src
    assert fixed == expected
