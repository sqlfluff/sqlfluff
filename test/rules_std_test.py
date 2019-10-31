""" The Test file for SQLFluff """

from sqlfluff.rules.std import standard_rule_set
from sqlfluff.linter import Linter


def get_rule_from_set(code):
    for r in standard_rule_set:
        if r.code == code:
            return r
    else:
        raise ValueError("{0!r} not in {1!r}".format(code, standard_rule_set))


def assert_rule_fail_in_sql(code, sql):
    r = get_rule_from_set(code)
    parsed, _, _ = Linter().parse_file(sql)
    print("Parsed:\n {0}".format(parsed.stringify()))
    lerrs, _, _, _ = r.crawl(parsed, fix=True)
    print("Errors Found: {0}".format(lerrs))
    assert any([v.rule.code == code for v in lerrs])
    fixes = []
    for e in lerrs:
        fixes += e.fixes
    print("Fixes to apply: {0}".format(fixes))
    while True:
        l_fixes = fixes
        fixed, fixes = parsed.apply_fixes(fixes)
        # iterate until all fixes applied
        if fixes:
            if fixes == l_fixes:
                raise RuntimeError(
                    "Fixes aren't being applied: {0!r}".format(fixes))
            else:
                continue
        else:
            break
    return fixed.raw


def assert_rule_pass_in_sql(code, sql):
    r = get_rule_from_set(code)
    parsed, _, _ = Linter().parse_file(sql)
    print("Parsed:\n {0}".format(parsed.stringify()))
    lerrs, _, _, _ = r.crawl(parsed, fix=True)
    print("Errors Found: {0}".format(lerrs))
    assert not any([v.rule.code == code for v in lerrs])


# ############## STD RULES TESTS
def test__rules__std__L001():
    res = assert_rule_fail_in_sql('L001', 'SELECT 1     \n')
    assert res == 'SELECT 1\n'


def test__rules__std__L002():
    assert_rule_fail_in_sql('L002', '    \t    \t    SELECT 1')


def test__rules__std__L003():
    assert_rule_fail_in_sql('L003', '     SELECT 1')


def test__rules__std__L004():
    assert_rule_pass_in_sql('L004', '   \nSELECT 1')
    assert_rule_pass_in_sql('L004', '\t\tSELECT 1\n')
    assert_rule_fail_in_sql('L004', '   \n  \t \n  SELECT 1')


def test__rules__std__L005():
    # L005 is about spaces before commas
    assert_rule_fail_in_sql('L005', 'SELECT 1 ,4')


def test__rules__std__L008():
    # L008 is about spaces after commas
    assert_rule_pass_in_sql('L008', 'SELECT 1, 4')
    assert_rule_fail_in_sql('L008', 'SELECT 1,   4')
