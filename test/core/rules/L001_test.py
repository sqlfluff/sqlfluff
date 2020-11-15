"""Tests for L001."""
import pytest

from .std_test import rules__test_helper, RuleTestCase

test_cases = []

test_cases.append(
    RuleTestCase(
        desc="Test unnecessary whitespace is removed",
        fail_str="""
        SELECT 1     
        """,  # noqa W291 so we keep the extra spaces
        fix_str="""
        SELECT 1
        """,
    )
)


@pytest.mark.parametrize("test_case", test_cases, ids=[t.desc for t in test_cases])
def test__rule_L001(test_case):
    """Run the tests."""
    rules__test_helper("L001", test_case)
