"""Runs the rule test cases."""

import os

import pytest

from sqlfluff.utils.testing.rules import (
    RuleTestCase,
    load_test_cases,
)

ids, test_cases = load_test_cases(
    test_cases_path=os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "test_cases", "*.yml"
    )
)


@pytest.mark.parametrize("test_case", test_cases, ids=ids)
def test__rule_test_case(test_case: RuleTestCase):
    """Evaluate the parameterized yaml test cases.

    NOTE: The test cases are loaded using `load_test_cases` above
    and then passed to this test case one by one. This allows fairly
    detailed rule testing, but defined only in the yaml files without
    any python overhead required.

    For examples of what features are available for parametrized rule
    testing, take a look at some of the test cases defined for the bundled
    SQLFluff core rules.
    """
    test_case.evaluate()
