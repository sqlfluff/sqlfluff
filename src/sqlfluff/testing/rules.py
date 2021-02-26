"""Testing utils for rule plugins."""
from sqlfluff.core import Linter
from sqlfluff.core.errors import SQLParseError
from sqlfluff.core.rules import get_ruleset
from sqlfluff.core.config import FluffConfig
from typing import Tuple, List, NamedTuple, Optional
from glob import glob

import pytest
import oyaml as yaml


class RuleTestCase(NamedTuple):
    """Used like a dataclass by rule tests."""

    rule: Optional[str] = None
    desc: Optional[str] = None
    pass_str: Optional[str] = None
    fail_str: Optional[str] = None
    fix_str: Optional[str] = None
    configs: Optional[dict] = None
    skip: Optional[str] = None


def load_test_cases(
    test_cases_path: str,
) -> Tuple[List[str], List[RuleTestCase]]:
    """Load rule test cases from YAML files."""
    ids = []
    test_cases = []

    for path in sorted(glob(test_cases_path)):
        with open(path) as f:
            raw = f.read()

        y = yaml.safe_load(raw)

        rule = y.pop("rule")
        ids.extend([rule + "_" + t for t in y])
        test_cases.extend([RuleTestCase(rule=rule, **v) for k, v in y.items()])

    return ids, test_cases


def get_rule_from_set(code, config):
    """Fetch a rule from the rule set."""
    for r in get_ruleset().get_rulelist(config=config):
        if r.code == code:
            return r
    raise ValueError("{0!r} not in {1!r}".format(code, get_ruleset()))


def assert_rule_fail_in_sql(code, sql, configs=None):
    """Assert that a given rule does fail on the given sql."""
    # Set up the config to only use the rule we are testing.
    cfg = FluffConfig(configs=configs, overrides={"rules": code})
    # Lint it using the current config (while in fix mode)
    linted = Linter(config=cfg).lint_string(sql, fix=True)
    lerrs = linted.get_violations()
    print("Errors Found: {0}".format(lerrs))
    parse_errors = list(filter(lambda v: type(v) == SQLParseError, lerrs))
    if parse_errors:
        pytest.fail(f"Found the following parse errors in test case: {parse_errors}")
    if not any(v.rule.code == code for v in lerrs):
        pytest.fail(
            "No {0} failures found in query which should fail.".format(code),
            pytrace=False,
        )
    # The query should already have been fixed if possible so just return the raw.
    return linted.tree.raw


def assert_rule_pass_in_sql(code, sql, configs=None):
    """Assert that a given rule doesn't fail on the given sql."""
    # Configs allows overrides if we want to use them.
    cfg = FluffConfig(configs=configs)
    r = get_rule_from_set(code, config=cfg)
    parsed = Linter(config=cfg).parse_string(sql)
    if parsed.violations:
        pytest.fail(parsed.violations[0].desc() + "\n" + parsed.tree.stringify())
    print("Parsed:\n {0}".format(parsed.tree.stringify()))
    lerrs, _, _, _ = r.crawl(parsed.tree, dialect=cfg.get("dialect_obj"))
    print("Errors Found: {0}".format(lerrs))
    if any(v.rule.code == code for v in lerrs):
        pytest.fail(
            "Found {0} failures in query which should pass.".format(code), pytrace=False
        )


def assert_rule_raises_violations_in_file(rule, fpath, violations, fluff_config):
    """Assert that a given rule raises given errors in specific positions of a file."""
    lntr = Linter(config=fluff_config)
    lnt = lntr.lint_path(fpath)
    # Reformat the test data to match the format we're expecting. We use
    # sets because we really don't care about order and if one is missing,
    # we don't care about the orders of the correct ones.
    assert set(lnt.check_tuples()) == {(rule, v[0], v[1]) for v in violations}


def rules__test_helper(test_case):
    """Test that a rule passes/fails on a set of test_cases.

    Optionally, also test the fixed string if provided in the test case.
    """
    if test_case.skip:
        pytest.skip(test_case.skip)

    if test_case.pass_str:
        assert_rule_pass_in_sql(
            test_case.rule,
            test_case.pass_str,
            configs=test_case.configs,
        )
    if test_case.fail_str:
        res = assert_rule_fail_in_sql(
            test_case.rule,
            test_case.fail_str,
            configs=test_case.configs,
        )
        # If a `fixed` value is provided then check it matches
        if test_case.fix_str:
            assert res == test_case.fix_str
