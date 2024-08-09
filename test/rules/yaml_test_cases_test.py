"""Runs the rule test cases."""

import logging
import os

import pytest

from sqlfluff.core.config import FluffConfig
from sqlfluff.utils.testing.rules import (
    get_rule_from_set,
    load_test_cases,
    rules__test_helper,
)


def pytest_generate_tests(metafunc):
    """Generate tests, optionally by rule_id."""
    rule_id = metafunc.config.getoption("rule_id")
    ids, test_cases = load_test_cases(
        test_cases_path=os.path.join(
            "test/fixtures/rules/std_rule_cases", f"{rule_id}.yml"
        )
    )
    if "test_case" in metafunc.fixturenames:
        metafunc.parametrize("test_case", test_cases, ids=ids)


@pytest.mark.integration
@pytest.mark.rules_suite
def test__rule_test_case(test_case, caplog):
    """Run the tests."""
    with caplog.at_level(logging.DEBUG, logger="sqlfluff.rules"):
        with caplog.at_level(logging.DEBUG, logger="sqlfluff.linter"):
            res = rules__test_helper(test_case)
            if res is not None and res != test_case.fail_str:
                cfg = FluffConfig(configs=test_case.configs)
                rule = get_rule_from_set(test_case.rule, config=cfg)
                assert rule.is_fix_compatible, f"Rule {test_case.rule} returned "
                'fixes but does not specify "is_fix_compatible = True".'


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
