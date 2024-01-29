"""Testing utils for rule plugins."""

from glob import glob
from typing import List, NamedTuple, Optional, Set, Tuple

import pytest
import yaml

from sqlfluff.core import Linter
from sqlfluff.core.config import FluffConfig
from sqlfluff.core.errors import SQLParseError, SQLTemplaterError
from sqlfluff.core.rules import BaseRule, get_ruleset


class RuleTestCase(NamedTuple):
    """Used like a dataclass by rule tests."""

    rule: Optional[str] = None
    desc: Optional[str] = None
    pass_str: Optional[str] = None
    fail_str: Optional[str] = None
    violations: Optional[Set[dict]] = None
    fix_str: Optional[str] = None
    violations_after_fix: Optional[Set[dict]] = None
    configs: Optional[dict] = None
    skip: Optional[str] = None
    line_numbers: List[int] = []


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
        global_config = y.pop("configs", None)
        if global_config:
            for i in y:
                if "configs" not in y[i].keys():
                    y[i].update({"configs": global_config})
        ids.extend([rule + "_" + t for t in y])
        test_cases.extend([RuleTestCase(rule=rule, **v) for k, v in y.items()])

    return ids, test_cases


def get_rule_from_set(code, config) -> BaseRule:
    """Fetch a rule from the rule set."""
    for r in get_ruleset().get_rulepack(config=config).rules:
        if r.code == code:  # pragma: no cover
            return r
    raise ValueError(f"{code!r} not in {get_ruleset()!r}")


def assert_rule_fail_in_sql(code, sql, configs=None, line_numbers=None):
    """Assert that a given rule does fail on the given sql."""
    print("# Asserting Rule Fail in SQL")
    # Set up the config to only use the rule we are testing.
    overrides = {"rules": code}
    if configs is None or "core" not in configs or "dialect" not in configs["core"]:
        overrides["dialect"] = "ansi"
    cfg = FluffConfig(configs=configs, overrides=overrides)
    # Lint it using the current config (while in fix mode)
    linted = Linter(config=cfg).lint_string(sql, fix=True)
    lerrs = linted.get_violations()
    print("Errors Found:")
    for e in lerrs:
        print("    " + repr(e))
        if e.desc().startswith("Unexpected exception"):
            pytest.fail(f"Linter failed with {e.desc()}")  # pragma: no cover
    parse_errors = list(
        filter(lambda v: isinstance(v, (SQLParseError, SQLTemplaterError)), lerrs)
    )
    if parse_errors:
        pytest.fail(f"Found the following parse errors in test case: {parse_errors}")
    if not any(v.rule.code == code for v in lerrs):
        assert linted.tree
        print(f"Parsed File:\n{linted.tree.stringify()}")
        pytest.fail(
            f"No {code} failures found in query which should fail.",
            pytrace=False,
        )
    if line_numbers:
        actual_line_numbers = [e.line_no for e in lerrs]
        if line_numbers != actual_line_numbers:  # pragma: no cover
            pytest.fail(
                "Expected errors on lines {}, but got errors on lines {}".format(
                    line_numbers, actual_line_numbers
                )
            )
    fixed, _ = linted.fix_string()
    return fixed, linted.violations


def assert_rule_pass_in_sql(code, sql, configs=None, msg=None):
    """Assert that a given rule doesn't fail on the given sql."""
    # Configs allows overrides if we want to use them.
    print("# Asserting Rule Pass in SQL")
    if configs is None:
        configs = {}
    core = configs.setdefault("core", {})
    core["rules"] = code
    overrides = {}
    if "dialect" not in configs["core"]:
        overrides["dialect"] = "ansi"
    cfg = FluffConfig(configs=configs, overrides=overrides)
    linter = Linter(config=cfg)

    # This section is mainly for aid in debugging.
    rendered = linter.render_string(sql, fname="<STR>", config=cfg, encoding="utf-8")
    parsed = linter.parse_rendered(rendered)
    if parsed.violations:
        if msg:
            print(msg)  # pragma: no cover
        assert parsed.tree
        pytest.fail(parsed.violations[0].desc() + "\n" + parsed.tree.stringify())
    assert parsed.tree
    print(f"Parsed:\n {parsed.tree.stringify()}")

    # Note that lint_string() runs the templater and parser again, in order to
    # test the whole linting pipeline in the same way that users do. In other
    # words, the "rendered" and "parsed" variables above are irrelevant to this
    # line of code.
    lint_result = linter.lint_string(sql, config=cfg, fname="<STR>")
    lerrs = lint_result.violations
    if any(v.rule.code == code for v in lerrs):
        print("Errors Found:")
        for e in lerrs:
            print("    " + repr(e))

        if msg:
            print(msg)  # pragma: no cover
        pytest.fail(f"Found {code} failures in query which should pass.", pytrace=False)


def assert_rule_raises_violations_in_file(rule, fpath, violations, fluff_config):
    """Assert that a given rule raises given errors in specific positions of a file."""
    lntr = Linter(config=fluff_config)
    lnt = lntr.lint_path(fpath)
    # Reformat the test data to match the format we're expecting. We use
    # sets because we really don't care about order and if one is missing,
    # we don't care about the orders of the correct ones.
    assert set(lnt.check_tuples()) == {(rule, v[0], v[1]) for v in violations}


def prep_violations(rule, violations):
    """Default to test rule if code is omitted."""
    for v in violations:
        if "code" not in v:
            v["code"] = rule
    return violations


def assert_violations_before_fix(test_case, violations_before_fix):
    """Assert that the given violations are found in the given sql."""
    print("# Asserting Violations Before Fix")
    violation_info = [e.to_dict() for e in violations_before_fix]
    try:
        assert violation_info == prep_violations(test_case.rule, test_case.violations)
    except AssertionError:  # pragma: no cover
        print("Actual violations:\n" + yaml.dump(violation_info))
        raise


def assert_violations_after_fix(test_case):
    """Assert that the given violations are found in the fixed sql."""
    print("# Asserting Violations After Fix")
    _, violations_after_fix = assert_rule_fail_in_sql(
        test_case.rule,
        test_case.fix_str,
        configs=test_case.configs,
        line_numbers=test_case.line_numbers,
    )
    violation_info = [e.to_dict() for e in violations_after_fix]
    try:
        assert violation_info == prep_violations(
            test_case.rule, test_case.violations_after_fix
        )
    except AssertionError:  # pragma: no cover
        print("Actual violations_after_fix:\n" + yaml.dump(violation_info))
        raise


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
        res, violations_before_fix = assert_rule_fail_in_sql(
            test_case.rule,
            test_case.fail_str,
            configs=test_case.configs,
            line_numbers=test_case.line_numbers,
        )
        if test_case.violations:
            assert_violations_before_fix(test_case, violations_before_fix)
        # If a `fixed` value is provided then check it matches
        if test_case.fix_str:
            assert res == test_case.fix_str
            if test_case.violations_after_fix:
                assert_violations_after_fix(test_case)
            else:
                assert_rule_pass_in_sql(
                    test_case.rule,
                    test_case.fix_str,
                    configs=test_case.configs,
                    msg="The SQL after fix is applied still contains rule violations. "
                    "To accept a partial fix, violations_after_fix must be set "
                    "listing the remaining, expected, violations.",
                )
        else:
            # Check that tests without a fix_str do not apply any fixes.
            assert res == test_case.fail_str, (
                "No fix_str was provided, but the rule modified the SQL. Where a fix "
                "can be applied by a rule, a fix_str must be supplied in the test."
            )
