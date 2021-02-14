"""Runs the rule test cases."""
import os
import pytest
from sqlfluff.testing.rules import load_test_cases, rules__test_helper

ids, test_cases = load_test_cases(
    test_cases_path=os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "test_cases", "*.yml"
    )
)


@pytest.mark.parametrize("test_case", test_cases, ids=ids)
def test__rule_test_case(test_case):
    """Run the tests."""
    rules__test_helper(test_case)
