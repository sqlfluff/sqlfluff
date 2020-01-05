"""Tests for the standard set of rules."""

import pytest

from sqlfluff.rules.std import std_rule_set
from sqlfluff.linter import Linter
from sqlfluff.config import FluffConfig


def get_rule_from_set(code):
    """Fetch a rule from the rule set."""
    for r in std_rule_set.get_rulelist(config=FluffConfig()):
        if r.code == code:
            return r
    else:
        raise ValueError("{0!r} not in {1!r}".format(code, std_rule_set))


def assert_rule_fail_in_sql(code, sql):
    """Assert that a given rule does fail on the given sql."""
    r = get_rule_from_set(code)
    parsed, _, _ = Linter(config=FluffConfig()).parse_string(sql)
    print("Parsed:\n {0}".format(parsed.stringify()))
    lerrs, _, _, _ = r.crawl(parsed, fix=True)
    print("Errors Found: {0}".format(lerrs))
    assert any([v.rule.code == code for v in lerrs])
    fixed = parsed  # use this as our buffer (yes it's a bit of misnomer right here)
    while True:
        # We get the errors again, but this time skip the assertion
        # because we're in the loop. If we asserted on every loop then
        # we're stuffed.
        lerrs, _, _, _ = r.crawl(fixed, fix=True)
        print("Errors Found: {0}".format(lerrs))
        fixes = []
        for e in lerrs:
            fixes += e.fixes
        if not fixes:
            print("Done")
            break
        print("Fixes to apply: {0}".format(fixes))
        l_fixes = fixes  # Save the fixes to compare to later
        fixed, fixes = fixed.apply_fixes(fixes)
        # iterate until all fixes applied
        if fixes:
            if fixes == l_fixes:
                raise RuntimeError(
                    "Fixes aren't being applied: {0!r}".format(fixes))
            else:
                continue
    return fixed.raw


def assert_rule_pass_in_sql(code, sql):
    """Assert that a given rule doesn't fail on the given sql."""
    r = get_rule_from_set(code)
    parsed, _, _ = Linter(config=FluffConfig()).parse_string(sql)
    print("Parsed:\n {0}".format(parsed.stringify()))
    lerrs, _, _, _ = r.crawl(parsed, fix=True)
    print("Errors Found: {0}".format(lerrs))
    assert not any([v.rule.code == code for v in lerrs])


# ############## STD RULES TESTS
@pytest.mark.parametrize("rule,pass_fail,qry,fixed", [
    ("L001", 'fail', 'SELECT 1     \n', 'SELECT 1\n'),
    ('L002', 'fail', '    \t    \t    SELECT 1', None),
    ('L003', 'fail', '     SELECT 1', '    SELECT 1'),
    ('L004', 'pass', '   \nSELECT 1', None),
    ('L004', 'pass', '\t\tSELECT 1\n', None),
    ('L004', 'fail', '   \n  \t \n  SELECT 1', None),
    ('L005', 'fail', 'SELECT 1 ,4', 'SELECT 1,4'),
    ('L008', 'pass', 'SELECT 1, 4', None),
    ('L008', 'fail', 'SELECT 1,   4', 'SELECT 1, 4'),
    ('L014', 'pass', 'SELECT a, b', None),
    ('L014', 'pass', 'SELECT A, B', None),
    ("L015", 'fail', 'SELECT DISTINCT(a)', None),
    ("L015", 'fail', 'SELECT DISTINCT(a + b) * c', None),
    # Space after DISTINCT makes it okay...
    ("L015", 'pass', 'SELECT DISTINCT (a)', None),  # A bit iffy...
    ("L015", 'pass', 'SELECT DISTINCT (a + b) * c', None),  # Definitely okay
    # Test that fixes are consistent
    ('L014', 'fail', 'SELECT a,   B', 'SELECT a,   b'),
    ('L014', 'fail', 'SELECT B,   a', 'SELECT B,   A'),
    # Test that we don't fail * operators in brackets
    ('L006', 'pass', 'SELECT COUNT(*) FROM tbl\n', None),
    # Test that we don't have the "inconsistent" bug
    ('L010', 'fail', 'SeLeCt 1', 'SELECT 1'),
    ('L010', 'fail', 'SeLeCt 1 from blah', 'SELECT 1 FROM blah'),
    # Gihub Bug #99. Python2 Issues with fixing L003
    ('L003', 'fail', '  select 1 from tbl;', 'select 1 from tbl;')
])
def test__rules__std_string(rule, pass_fail, qry, fixed):
    """Test that a rule passes/fails on a given string.

    Optionally, also test the fixed string if provided.
    """
    if pass_fail == 'fail':
        res = assert_rule_fail_in_sql(rule, qry)
        # If a `fixed` value is provided then check it matches
        if fixed:
            assert res == fixed
    elif pass_fail == 'pass':
        assert_rule_pass_in_sql(rule, qry)
    else:
        raise ValueError(
            "Test setup fail: Unexpected value for pass_fail: {0!r}".format(
                pass_fail))


@pytest.mark.parametrize("rule,path,violations", [
    ('L001', 'test/fixtures/linter/indentation_errors.sql', [(4, 24)]),
    ('L002', 'test/fixtures/linter/indentation_errors.sql', [(3, 1), (4, 1)]),
    ('L003', 'test/fixtures/linter/indentation_errors.sql', [(2, 1), (3, 1)]),
    ('L004', 'test/fixtures/linter/indentation_errors.sql', [(3, 1), (4, 1), (5, 1)]),
    # Check we get comma (with leading space/newline) whitespace errors
    # NB The newline before the comma, should report on the comma, not the newline for clarity.
    ('L005', 'test/fixtures/linter/whitespace_errors.sql', [(2, 9), (4, 1)]),
    # Check we get comma (with incorrect trailing space) whitespace errors,
    # but also no false positives on line 4 or 5.
    ('L008', 'test/fixtures/linter/whitespace_errors.sql', [(3, 12)]),
    # Check we get operator whitespace errors and it works with brackets
    ('L006', 'test/fixtures/linter/operator_errors.sql',
     [(3, 8), (4, 10), (7, 6), (7, 7), (7, 9), (7, 10), (7, 12), (7, 13)]),
    ('L007', 'test/fixtures/linter/operator_errors.sql', [(5, 9)]),
    # Check we DO get a violation on line 2 but NOT on line 3
    ('L006', 'test/fixtures/linter/operator_errors_negative.sql', [(2, 6), (2, 9), (5, 6), (5, 7)])
])
def test__rules__std_file(rule, path, violations):
    """Test the linter finds the given errors in (and only in) the right places."""
    # Use config to look for only the rule we care about.
    lntr = Linter(config=FluffConfig(overrides=dict(rules=rule)))
    lnt = lntr.lint_path(path)
    # Reformat the test data to match the format we're expecting. We use
    # sets because we really don't care about order and if one is missing,
    # we don't care about the orders of the correct ones.
    assert set(lnt.check_tuples()) == set([(rule, v[0], v[1]) for v in violations])
