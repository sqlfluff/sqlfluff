"""Testing utils for rule plugins."""

from glob import glob
from typing import (
    Collection,
    Dict,
    List,
    NamedTuple,
    Optional,
    Set,
    Tuple,
    Union,
)

import pytest
import yaml

from sqlfluff.core import Linter
from sqlfluff.core.config import FluffConfig
from sqlfluff.core.errors import (
    SQLBaseError,
    SQLLintError,
    SQLParseError,
    SQLTemplaterError,
)
from sqlfluff.core.rules import BaseRule, get_ruleset
from sqlfluff.core.types import ConfigMappingType

FixDictType = Dict[str, Union[str, int]]
ViolationDictType = Dict[str, Union[str, int, bool, List[FixDictType]]]


class RuleTestCase(NamedTuple):
    """Used like a dataclass by rule tests."""

    rule: str
    desc: Optional[str] = None
    pass_str: Optional[str] = None
    fail_str: Optional[str] = None
    violations: Optional[Set[ViolationDictType]] = None
    fix_str: Optional[str] = None
    violations_after_fix: Optional[Set[ViolationDictType]] = None
    configs: Optional[ConfigMappingType] = None
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


def get_rule_from_set(code: str, config: FluffConfig) -> BaseRule:
    """Fetch a rule from the rule set."""
    for r in get_ruleset().get_rulepack(config=config).rules:
        if r.code == code:  # pragma: no cover
            return r
    raise ValueError(f"{code!r} not in {get_ruleset()!r}")


def _setup_config(
    code: str, configs: Optional[ConfigMappingType] = None
) -> FluffConfig:
    """Helper function to set up config consistently for pass & fail functions."""
    overrides: ConfigMappingType = {"rules": code}
    _core_section = configs.get("core", {}) if configs else {}
    if not isinstance(_core_section, dict) or "dialect" not in _core_section:
        overrides["dialect"] = "ansi"
    return FluffConfig(configs=configs, overrides=overrides)


def assert_rule_fail_in_sql(
    code: str,
    sql: str,
    configs: Optional[ConfigMappingType] = None,
    line_numbers: Optional[List[int]] = None,
) -> Tuple[str, List[SQLBaseError]]:
    """Assert that a given rule does fail on the given sql."""
    print("# Asserting Rule Fail in SQL")
    # Set up the config to only use the rule we are testing.
    cfg = _setup_config(code, configs)
    # Lint it using the current config (while in fix mode)
    linted = Linter(config=cfg).lint_string(sql, fix=True)
    all_violations = linted.get_violations()
    print("Errors Found:")
    for e in all_violations:
        print("    " + repr(e))
        if e.desc().startswith("Unexpected exception"):
            pytest.fail(f"Linter failed with {e.desc()}")  # pragma: no cover
    parse_errors = [
        v for v in all_violations if isinstance(v, (SQLParseError, SQLTemplaterError))
    ]
    if parse_errors:
        pytest.fail(f"Found the following parse errors in test case: {parse_errors}")
    lint_errors: List[SQLLintError] = [
        v for v in all_violations if isinstance(v, SQLLintError)
    ]
    if not any(v.rule.code == code for v in lint_errors):
        assert linted.tree
        print(f"Parsed File:\n{linted.tree.stringify()}")
        pytest.fail(
            f"No {code} failures found in query which should fail.",
            pytrace=False,
        )
    if line_numbers:
        actual_line_numbers = [e.line_no for e in lint_errors]
        if line_numbers != actual_line_numbers:  # pragma: no cover
            pytest.fail(
                "Expected errors on lines {}, but got errors on lines {}".format(
                    line_numbers, actual_line_numbers
                )
            )
    fixed, _ = linted.fix_string()
    return fixed, linted.violations


def assert_rule_pass_in_sql(
    code: str,
    sql: str,
    configs: Optional[ConfigMappingType] = None,
    msg: Optional[str] = None,
) -> None:
    """Assert that a given rule doesn't fail on the given sql."""
    # Configs allows overrides if we want to use them.
    print("# Asserting Rule Pass in SQL")
    cfg = _setup_config(code, configs)
    linter = Linter(config=cfg)

    # This section is mainly for aid in debugging.
    rendered = linter.render_string(sql, fname="<STR>", config=cfg, encoding="utf-8")
    parsed = linter.parse_rendered(rendered)
    tree = parsed.tree  # Delegate assertions to the `.tree` property
    violations = parsed.violations
    if violations:
        if msg:
            print(msg)  # pragma: no cover
        pytest.fail(violations[0].desc() + "\n" + tree.stringify())
    print(f"Parsed:\n {tree.stringify()}")

    # Note that lint_string() runs the templater and parser again, in order to
    # test the whole linting pipeline in the same way that users do. In other
    # words, the "rendered" and "parsed" variables above are irrelevant to this
    # line of code.
    lint_result = linter.lint_string(sql, config=cfg, fname="<STR>")
    lint_errors = [v for v in lint_result.violations if isinstance(v, SQLLintError)]
    if any(v.rule.code == code for v in lint_errors):
        print("Errors Found:")
        for e in lint_result.violations:
            print("    " + repr(e))

        if msg:
            print(msg)  # pragma: no cover
        pytest.fail(f"Found {code} failures in query which should pass.", pytrace=False)


def assert_rule_raises_violations_in_file(
    rule: str, fpath: str, violations: List[Tuple[int, int]], fluff_config: FluffConfig
) -> None:
    """Assert that a given rule raises given errors in specific positions of a file.

    Args:
        rule (str): The rule we're looking for.
        fpath (str): The path to the sql file to check.
        violations (:obj:`list` of :obj:`tuple`): A list of tuples, each with the line
            number and line position of the expected violation.
        fluff_config (:obj:`FluffConfig`): A config object to use while linting.
    """
    lntr = Linter(config=fluff_config)
    lnt = lntr.lint_path(fpath)
    # Reformat the test data to match the format we're expecting. We use
    # sets because we really don't care about order and if one is missing,
    # we don't care about the orders of the correct ones.
    assert set(lnt.check_tuples()) == {(rule, v[0], v[1]) for v in violations}


def prep_violations(
    rule: str, violations: Collection[ViolationDictType]
) -> Collection[ViolationDictType]:
    """Default to test rule if code is omitted."""
    for v in violations:
        if "code" not in v:
            v["code"] = rule
    return violations


def assert_violations_before_fix(
    test_case: RuleTestCase, violations_before_fix: List[SQLBaseError]
) -> None:
    """Assert that the given violations are found in the given sql."""
    print("# Asserting Violations Before Fix")
    violation_info = [e.to_dict() for e in violations_before_fix]
    assert (
        test_case.violations
    ), "Test case must have `violations` to call `assert_violations_before_fix()`"
    try:
        assert violation_info == prep_violations(test_case.rule, test_case.violations)
    except AssertionError:  # pragma: no cover
        print("Actual violations:\n" + yaml.dump(violation_info))
        raise


def assert_violations_after_fix(test_case: RuleTestCase) -> None:
    """Assert that the given violations are found in the fixed sql."""
    print("# Asserting Violations After Fix")
    assert (
        test_case.fix_str
    ), "Test case must have `fix_str` to call `assert_violations_after_fix()`"
    assert test_case.violations_after_fix, (
        "Test case must have `violations_after_fix` to call "
        "`assert_violations_after_fix()`"
    )
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


def rules__test_helper(test_case: RuleTestCase) -> None:
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
