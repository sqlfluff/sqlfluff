"""Runs the rule test cases."""
import os
from glob import glob

import pytest
import oyaml as yaml

from sqlfluff.core.config import FluffConfig
from sqlfluff.core.rules.doc_decorators import is_fix_compatible
from .std_test import get_rule_from_set, rules__test_helper, RuleTestCase

ids = []
test_cases = []

test_cases_path = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), "test_cases", "*.yml"
)

for path in sorted(glob(test_cases_path)):
    with open(path) as f:
        raw = f.read()

    y = yaml.safe_load(raw)

    rule = y.pop("rule")
    ids.extend([rule + "_" + t for t in y])
    test_cases.extend([RuleTestCase(rule=rule, **v) for k, v in y.items()])


@pytest.mark.parametrize("test_case", test_cases, ids=ids)
def test__rule_test_case(test_case):
    """Run the tests."""
    res = rules__test_helper(test_case)
    if res is not None and res != test_case.fail_str:
        cfg = FluffConfig(configs=test_case.configs)
        rule = get_rule_from_set(test_case.rule, config=cfg)
        assert is_fix_compatible(
            rule
        ), f'Rule {test_case.rule} returned fixes but does not specify "@document_fix_compatible".'
