"""Runs the rule test cases."""
import os
import glob

import pytest
import oyaml as yaml

from .std_test import rules__test_helper, RuleTestCase

ids = []
test_cases = []

test_cases_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test_cases', '*.yml')
for path in glob.glob(test_cases_path):
    with open(path) as f:
        raw = f.read()

    y = yaml.safe_load(raw)

    rule = y['rule']
    named_tests = {k: v for k, v in y.items() if k.startswith('test')}
    ids.extend([rule + '_' + t for t in named_tests])
    test_cases.extend([RuleTestCase(rule=rule, **v) for k, v in named_tests.items()])


@pytest.mark.parametrize("test_case", test_cases, ids=ids)
def test__rule_test_case(test_case):
    """Run the tests."""
    rules__test_helper(test_case)
