"""Runs the rule test cases."""

import logging
import os

import pytest

from sqlfluff.utils.testing.rules import (
    RuleTestCase,
    load_test_cases,
)


def pytest_generate_tests(metafunc):
    """Generate yaml test cases from file.

    This is a predefined pytest hook which allows us to parametrize all
    other test cases defined in this module.
    https://docs.pytest.org/en/stable/how-to/parametrize.html#pytest-generate-tests
    """
    ids, test_cases = load_test_cases(
        test_cases_path="test/fixtures/rules/std_rule_cases/*.yml"
    )
    # Only parametrize methods which include `test_case` in their
    # list of required fixtures.
    if "test_case" in metafunc.fixturenames:
        metafunc.parametrize("test_case", test_cases, ids=ids)


@pytest.mark.integration
@pytest.mark.rules_suite
def test__rule_test_case(test_case: RuleTestCase, caplog):
    """Execute each of the rule test cases.

    The cases themselves are parametrized using the above
    `pytest_generate_tests` function, which both loads them
    from the yaml files do generate `RuleTestCase` objects,
    but also sets appropriate IDs for each test to improve the
    user feedback.
    """
    with caplog.at_level(logging.DEBUG, logger="sqlfluff.rules"):
        with caplog.at_level(logging.DEBUG, logger="sqlfluff.linter"):
            test_case.evaluate()


def test__rule_test_global_config():
    """Test global config in rule test cases."""
    ids, test_cases = load_test_cases(
        os.path.join("test/fixtures/rules/R001_global_config_test.yml")
    )
    assert len(test_cases) == 2
    # tc1: overwrites global config
    assert test_cases[0].configs["core"]["dialect"] == "ansi"
    # tc2: global config is used
    assert test_cases[1].configs["core"]["dialect"] == "exasol"
