"""Runs the rule test cases."""

import copy
import logging
import os

import pytest

from sqlfluff.core import Linter
from sqlfluff.utils.testing.rules import (
    RuleTestCase,
    _setup_config,
    load_test_cases,
    rules__test_helper,
)

try:
    from sqlfluff.core.parser.rust_parser import _HAS_RUST_PARSER
except ImportError:
    _HAS_RUST_PARSER = False


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


def _rust_configs(test_case: RuleTestCase, use_rust_rules: bool):
    configs = copy.deepcopy(test_case.configs or {})
    core = configs.setdefault("core", {})
    assert isinstance(core, dict)
    core.update(use_rust_parser=True, use_rust_rules=use_rust_rules)
    return configs


def _lint(test_case: RuleTestCase, sql: str, use_rust_rules: bool):
    cfg = _setup_config(test_case.rule, _rust_configs(test_case, use_rust_rules))
    linted = Linter(config=cfg).lint_string(sql, fix=True)
    return [v.to_dict() for v in linted.get_violations()], linted.fix_string()[0]


@pytest.mark.integration
@pytest.mark.rules_suite
def test__rule_test_case_rust(test_case: RuleTestCase):
    """Each rule case with Rust rules on: it meets the case, and matches Python.

    Parity compares violations (positions, descriptions, fixes) and the fixed
    source.
    """
    if not _HAS_RUST_PARSER:
        # The -rust tox envs must not silently skip this.
        if os.environ.get("TOX_ENV_NAME", "").endswith("-rust"):
            pytest.fail("sqlfluffrs is not installed in a -rust env")
        pytest.skip("sqlfluffrs not installed")
    rules__test_helper(test_case._replace(configs=_rust_configs(test_case, True)))
    for sql in (test_case.pass_str, test_case.fail_str):
        if sql:
            assert _lint(test_case, sql, True) == _lint(test_case, sql, False), sql


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
