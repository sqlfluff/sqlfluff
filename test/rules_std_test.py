"""Tests for the standard set of rules."""

import pytest

from sqlfluff.rules.base import BaseCrawler
from sqlfluff.rules.std import std_rule_set
from sqlfluff.rules.config import document_configuration
from sqlfluff.linter import Linter
from sqlfluff.config import FluffConfig


def get_rule_from_set(code, config):
    """Fetch a rule from the rule set."""
    for r in std_rule_set.get_rulelist(config=config):
        if r.code == code:
            return r
    raise ValueError("{0!r} not in {1!r}".format(code, std_rule_set))


def assert_rule_fail_in_sql(code, sql, configs=None):
    """Assert that a given rule does fail on the given sql."""
    # Configs allows overrides if we want to use them.
    cfg = FluffConfig(configs=configs)
    r = get_rule_from_set(code, config=cfg)
    parsed, _, _ = Linter(config=cfg).parse_string(sql)
    print("Parsed:\n {0}".format(parsed.stringify()))
    lerrs, _, _, _ = r.crawl(parsed, dialect=cfg.get('dialect_obj'), fix=True)
    print("Errors Found: {0}".format(lerrs))
    if not any(v.rule.code == code for v in lerrs):
        pytest.fail(
            "No {0} failures found in query which should fail.".format(code),
            pytrace=False)
    fixed = parsed  # use this as our buffer (yes it's a bit of misnomer right here)
    while True:
        # We get the errors again, but this time skip the assertion
        # because we're in the loop. If we asserted on every loop then
        # we're stuffed.
        lerrs, _, _, _ = r.crawl(fixed, dialect=cfg.get('dialect_obj'), fix=True)
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
    return fixed.raw


def assert_rule_pass_in_sql(code, sql, configs=None):
    """Assert that a given rule doesn't fail on the given sql."""
    # Configs allows overrides if we want to use them.
    cfg = FluffConfig(configs=configs)
    r = get_rule_from_set(code, config=cfg)
    parsed, _, _ = Linter(config=cfg).parse_string(sql)
    print("Parsed:\n {0}".format(parsed.stringify()))
    lerrs, _, _, _ = r.crawl(parsed, dialect=cfg.get('dialect_obj'), fix=True)
    print("Errors Found: {0}".format(lerrs))
    if any(v.rule.code == code for v in lerrs):
        pytest.fail(
            "Found {0} failures in query which should pass.".format(code),
            pytrace=False)


# ############## STD RULES TESTS
@pytest.mark.parametrize("rule,pass_fail,qry,fixed,configs", [
    ("L001", 'fail', 'SELECT 1     \n', 'SELECT 1\n', None),
    ('L002', 'fail', '    \t    \t    SELECT 1', None, None),
    ('L003', 'fail', '     SELECT 1', 'SELECT 1', None),
    ('L004', 'pass', '   \nSELECT 1', None, None),
    ('L004', 'pass', '\t\tSELECT 1\n', None, None),
    ('L004', 'fail', '   \n  \t \n  SELECT 1', None, None),
    ('L005', 'fail', 'SELECT 1 ,4', 'SELECT 1,4', None),
    ('L008', 'pass', 'SELECT 1, 4', None, None),
    ('L008', 'fail', 'SELECT 1,   4', 'SELECT 1, 4', None),
    ('L013', 'pass', 'SELECT *, foo from blah', None, None),
    ('L013', 'fail', 'SELECT upper(foo), bar from blah', None, None),
    ('L013', 'pass', 'SELECT upper(foo) as foo_up, bar from blah', None, None),
    ('L014', 'pass', 'SELECT a, b', None, None),
    ('L014', 'pass', 'SELECT A, B', None, None),
    # Check we get fails for using DISTINCT apparently incorrectly
    ("L015", 'fail', 'SELECT DISTINCT(a)', None, None),
    ("L015", 'fail', 'SELECT DISTINCT(a + b) * c', None, None),
    # Space after DISTINCT makes it okay...
    ("L015", 'pass', 'SELECT DISTINCT (a)', None, None),  # A bit iffy...
    ("L015", 'pass', 'SELECT DISTINCT (a + b) * c', None, None),  # Definitely okay
    # Test that fixes are consistent
    ('L014', 'fail', 'SELECT a,   B', 'SELECT a,   b', None),
    ('L014', 'fail', 'SELECT B,   a', 'SELECT B,   A', None),
    # Test that NULL is classed as a keyword and not an identifier
    ('L014', 'pass', 'SELECT NULL,   a', None, None),
    ('L010', 'fail', 'SELECT null,   a', 'SELECT NULL,   a', None),
    # Test that we don't fail * operators in brackets
    ('L006', 'pass', 'SELECT COUNT(*) FROM tbl\n', None, None),
    # Long lines (with config override)
    ('L016', 'pass', 'SELECT COUNT(*) FROM tbl\n', None,
     {'rules': {'max_line_length': 30}}),
    # Check we move comments correctly
    ('L016', 'fail', 'SELECT 1 -- Some Comment\n',
     '-- Some Comment\nSELECT 1\n',
     {'rules': {'max_line_length': 18}}),
    # Check we can add newlines after dedents (with an indent)
    ('L016', 'fail', '    SELECT COUNT(*) FROM tbl\n',
     '    SELECT\n        COUNT(*)\n    FROM tbl\n',
     {'rules': {'max_line_length': 20}}),
    # Check we handle indents nicely
    ('L016', 'fail', 'SELECT 12345\n',
     'SELECT\n    12345\n',
     {'rules': {'max_line_length': 10}}),
    # Check priority of fixes
    ('L016', 'fail', 'SELECT COUNT(*) FROM tbl -- Some Comment\n',
     '-- Some Comment\nSELECT\n    COUNT(*)\nFROM tbl\n',
     {'rules': {'max_line_length': 18}}),
    # Test that we don't have the "inconsistent" bug
    ('L010', 'fail', 'SeLeCt 1', 'SELECT 1', None),
    ('L010', 'fail', 'SeLeCt 1 from blah', 'SELECT 1 FROM blah', None),
    # Github Bug #99. Python2 Issues with fixing L003
    ('L003', 'fail', '  select 1 from tbl;', 'select 1 from tbl;', None),
    # Github Bug #207
    ('L006', 'pass', "select\n    field,\n    date(field_1) - date(field_2) as diff\nfrom table", None, None),
    # Github Bug #203
    ('L003', 'pass', "SELECT\n    -- Compute the thing\n    (a + b) AS c\nFROM\n    acceptable_buckets", None, None),
    ('L003', 'pass',
     ("SELECT\n    user_id\nFROM\n    age_data\nJOIN\n    audience_size\n    USING (user_id, list_id)\n"
      "-- We LEFT JOIN because blah\nLEFT JOIN\n    verts\n    USING\n        (user_id)"),
     None, None),
    # Leading commas
    ('L019', 'fail', 'SELECT\n    a\n    , b\n    FROM c', None,
     {'rules': {'L019': {'comma_style': 'trailing'}}}),
    ('L019', 'pass', 'SELECT\n    a\n    , b\n    FROM c', None,
     {'rules': {'L019': {'comma_style': 'leading'}}}),
    # Leading commas in with statement
    ('L019', 'fail', ('WITH cte_1 as (\n    SELECT *\n    FROM table_1\n)\n\n'
                      ', cte_2 as (\n    SELECT *\n    FROM table_2\n)\n\n'
                      'SELECT * FROM table_3'), None,
        {'rules': {'L019': {'comma_style': 'trailing'}}}),
    ('L019', 'pass', ('WITH cte_1 as (\n    SELECT *\n    FROM table_1\n)\n\n'
                      ', cte_2 as (\n    SELECT *\n    FROM table_2\n)\n\n'
                      'SELECT * FROM table_3'), None,
        {'rules': {'L019': {'comma_style': 'leading'}}}),
    # Trailing commas
    ('L019', 'fail', 'SELECT\n    a,\n    b\n    FROM c', None,
     {'rules': {'L019': {'comma_style': 'leading'}}}),
    ('L019', 'pass', 'SELECT\n    a,\n    b\n    FROM c', None,
     {'rules': {'L019': {'comma_style': 'trailing'}}}),
    # Configurable indents work.
    # a) default
    ('L003', 'pass', 'SELECT a, b, c\nFROM my_tbl\nLEFT JOIN another_tbl USING(a)', None, None),
    # b) specific
    ('L003', 'pass', 'SELECT a, b, c\nFROM my_tbl\nLEFT JOIN another_tbl USING(a)', None,
     {'indentation': {'indented_joins': False}}),
    # c) specific True, but passing
    ('L003', 'pass', 'SELECT a, b, c\nFROM my_tbl\n    LEFT JOIN another_tbl USING(a)', None,
     {'indentation': {'indented_joins': True}}),
    # d) specific True, but failing
    ('L003', 'fail',
     'SELECT a, b, c\nFROM my_tbl\nLEFT JOIN another_tbl USING(a)',
     'SELECT a, b, c\nFROM my_tbl\n    LEFT JOIN another_tbl USING(a)',
     {'indentation': {'indented_joins': True}}),
    # e) specific False, and failing
    ('L003', 'fail',
     'SELECT a, b, c\nFROM my_tbl\n    LEFT JOIN another_tbl USING(a)',
     'SELECT a, b, c\nFROM my_tbl\nLEFT JOIN another_tbl USING(a)',
     {'indentation': {'indented_joins': False}}),
    # Check fixing of single space rules
    ('L023', 'fail', 'WITH a AS(select 1) select * from a', 'WITH a AS (select 1) select * from a', None),
    ('L024', 'fail', 'select * from a JOIN b USING(x)', 'select * from a JOIN b USING (x)', None),
    # Check L024 passes if there's a newline between
    ('L024', 'pass', 'select * from a JOIN b USING\n(x)', None, None),
    # References in quotes in biquery
    ('L026', 'pass', 'SELECT bar.user_id FROM `foo.far.bar`', None, {'core': {'dialect': 'bigquery'}}),
    ('L026', 'fail', 'SELECT foo.user_id FROM `foo.far.bar`', None, {'core': {'dialect': 'bigquery'}}),
    # Mixed qualification of references.
    ('L028', 'fail', 'SELECT my_tbl.bar, baz FROM my_tbl', None, None),
    ('L028', 'pass', 'SELECT bar FROM my_tbl', None, None),
    ('L028', 'pass', 'SELECT my_tbl.bar FROM my_tbl', None, None),
    ('L028', 'fail', 'SELECT my_tbl.bar FROM my_tbl', None, {'rules': {'L028': {'single_table_references': 'unqualified'}}}),
    ('L028', 'fail', 'SELECT bar FROM my_tbl', None, {'rules': {'L028': {'single_table_references': 'qualified'}}}),
    # References in WHERE clause
    ('L026', 'fail', 'SELECT * FROM my_tbl WHERE foo.bar > 0', None, None),
    # Aliases not referenced.
    ('L025', 'fail', 'SELECT * FROM my_tbl AS foo', None, None),
    ('L025', 'pass', 'SELECT * FROM my_tbl AS foo JOIN other_tbl on other_tbl.x = foo.x', None, None),
    # Test cases for L029
    ('L029', 'pass', 'CREATE TABLE artist(artist_name TEXT)', None, None),
    ('L029', 'fail', 'CREATE TABLE artist(create TEXT)', None, None),
    ('L029', 'fail', 'SELECT 1 as parameter', None, None),
    ('L029', 'pass', 'SELECT parameter', None, None),  # should pass on default config as not alias
    ('L029', 'fail', 'SELECT parameter', None, {'rules': {'L029': {'only_aliases': False}}}),
    # Inconsistent capitalisation of functions
    ('L030', 'fail', 'SELECT MAX(id), min(id) from table', 'SELECT MAX(id), MIN(id) from table', None),
    ('L030', 'fail', 'SELECT MAX(id), min(id) from table', 'SELECT max(id), min(id) from table',
     {'rules': {'L030': {'capitalisation_policy': 'lower'}}}),
    # Check we don't get false alarms with newlines, or sign indicators.
    ('L006', 'pass', 'SELECT 1\n+ 2', None, None),
    ('L006', 'pass', 'SELECT 1\n\t+ 2', None, None),
    ('L006', 'pass', 'SELECT 1\n    + 2', None, None),
    ('L006', 'pass', 'SELECT 1, +2, -4', None, None),
    # Catch issues with subqueries properly
    ('L028', 'pass', 'SELECT * FROM db.sc.tbl2\nWHERE a NOT IN (SELECT a FROM db.sc.tbl1)\n', None, None),
    ('L026', 'pass', 'SELECT * FROM db.sc.tbl2\nWHERE a NOT IN (SELECT a FROM db.sc.tbl1)\n', None, None),
    ('L026', 'pass', 'SELECT * FROM db.sc.tbl2\nWHERE a NOT IN (SELECT tbl2.a FROM db.sc.tbl1)\n', None, None),  # Correlated subquery.
    # Make sure comments are aligned properly
    ('L003', 'pass', 'SELECT *\nFROM\n    t1\n-- Comment\nJOIN t2 USING (user_id)', None, None),
    ('L003', 'fail', 'SELECT *\nFROM\n    t1\n    -- Comment\nJOIN t2 USING (user_id)', 'SELECT *\nFROM\n    t1\n-- Comment\nJOIN t2 USING (user_id)', None),
    # L013 & L025 Fixes with https://github.com/sqlfluff/sqlfluff/issues/449
    ('L013', 'pass', 'select ps.*, pandgs.blah from ps join pandgs using(moo)', None, None),
    ('L025', 'pass', 'select ps.*, pandgs.blah from ps join pandgs using(moo)', None, None)
])
def test__rules__std_string(rule, pass_fail, qry, fixed, configs):
    """Test that a rule passes/fails on a given string.

    Optionally, also test the fixed string if provided.
    """
    if pass_fail == 'fail':
        res = assert_rule_fail_in_sql(rule, qry, configs=configs)
        # If a `fixed` value is provided then check it matches
        if fixed:
            assert res == fixed
    elif pass_fail == 'pass':
        assert_rule_pass_in_sql(rule, qry, configs=configs)
    else:
        raise ValueError(
            "Test setup fail: Unexpected value for pass_fail: {0!r}".format(
                pass_fail))


@pytest.mark.parametrize("rule,path,violations", [
    ('L001', 'test/fixtures/linter/indentation_errors.sql', [(4, 24)]),
    ('L002', 'test/fixtures/linter/indentation_errors.sql', [(3, 1), (4, 1)]),
    ('L003', 'test/fixtures/linter/indentation_errors.sql', [(2, 4), (3, 4), (4, 6)]),
    ('L004', 'test/fixtures/linter/indentation_errors.sql', [(3, 1), (4, 1), (5, 1)]),
    # Check we get comma (with leading space/newline) whitespace errors
    # NB The newline before the comma, should report on the comma, not the newline for clarity.
    ('L005', 'test/fixtures/linter/whitespace_errors.sql', [(2, 9)]),
    ('L019', 'test/fixtures/linter/whitespace_errors.sql', [(4, 1)]),
    # Check we get comma (with incorrect trailing space) whitespace errors,
    # but also no false positives on line 4 or 5.
    ('L008', 'test/fixtures/linter/whitespace_errors.sql', [(3, 12)]),
    # Check we get operator whitespace errors and it works with brackets
    ('L006', 'test/fixtures/linter/operator_errors.sql',
     [(3, 8), (4, 10), (7, 6), (7, 7), (7, 9), (7, 10), (7, 12), (7, 13)]),
    ('L007', 'test/fixtures/linter/operator_errors.sql', [(5, 9)]),
    # Check we DO get a violation on line 2 but NOT on line 3
    ('L006', 'test/fixtures/linter/operator_errors_negative.sql', [(2, 6), (2, 9), (5, 6), (5, 7)]),
    # Hard indentation errors
    ('L003', 'test/fixtures/linter/indentation_error_hard.sql', [(2, 4), (6, 5), (9, 13), (14, 14), (19, 5), (20, 6)]),
    # Check bracket handling with closing brackets and contained indents works.
    ('L003', 'test/fixtures/linter/indentation_error_contained.sql', []),
    # Check we handle block comments as expect. Github #236
    ('L016', 'test/fixtures/linter/block_comment_errors.sql', [(1, 121), (2, 99), (4, 88)]),
    ('L016', 'test/fixtures/linter/block_comment_errors_2.sql', [(1, 85), (2, 86)]),
    # Column references
    ('L027', 'test/fixtures/linter/column_references.sql', [(1, 8)]),
    ('L027', 'test/fixtures/linter/column_references_bare_function.sql', []),
    ('L026', 'test/fixtures/linter/column_references.sql', [(1, 11)]),
    ('L025', 'test/fixtures/linter/column_references.sql', [(2, 11)]),
    # Distinct and Group by
    ('L021', 'test/fixtures/linter/select_distinct_group_by.sql', [(1, 8)]),
    # Make sure that ignoring works as expected
    ('L006', 'test/fixtures/linter/operator_errors_ignore.sql', [(10, 8), (10, 9)]),
])
def test__rules__std_file(rule, path, violations):
    """Test the linter finds the given errors in (and only in) the right places."""
    # Use config to look for only the rule we care about.
    lntr = Linter(config=FluffConfig(overrides=dict(rules=rule)))
    lnt = lntr.lint_path(path)
    # Reformat the test data to match the format we're expecting. We use
    # sets because we really don't care about order and if one is missing,
    # we don't care about the orders of the correct ones.
    assert set(lnt.check_tuples()) == {(rule, v[0], v[1]) for v in violations}


def test__rules__std_L003_process_raw_stack(generate_test_segments):
    """Test the _process_raw_stack function.

    Note: This test probably needs expanding. It doesn't
    really check enough of the full functionality.

    """
    cfg = FluffConfig()
    r = get_rule_from_set('L003', config=cfg)
    test_stack = generate_test_segments(['bar', '\n', '     ', 'foo', 'baar', ' \t '])
    res = r._process_raw_stack(test_stack)
    print(res)
    assert sorted(res.keys()) == [1, 2]
    assert res[2]['indent_size'] == 5


@pytest.mark.parametrize("rule_config_dict", [
    {"tab_space_size": "blah"},
    {"max_line_length": "blah"},
    {"indent_unit": "blah"},
    {"comma_style": "blah"},
    {"allow_scalar": "blah"},
    {"single_table_references": "blah"},
    {"only_aliases": "blah"},
    {"L010": {"capitalisation_policy": "blah"}},
    {"L014": {"capitalisation_policy": "blah"}},
    {"L030": {"capitalisation_policy": "blah"}},
])
def test_improper_configs_are_rejected(rule_config_dict):
    """Ensure that unsupported configs raise a ValueError."""
    config = FluffConfig(configs={"rules": rule_config_dict})
    with pytest.raises(ValueError):
        std_rule_set.get_rulelist(config)


def test_rules_must_be_instantiated_without_declared_configs():
    """Ensure that new rules must be instantiated with config values."""
    class NewRule(BaseCrawler):
        config_keywords = ["comma_style"]

    new_rule = NewRule(code="L000", description="", comma_style="trailing")
    assert new_rule.comma_style == "trailing"
    # Error is thrown since "comma_style" is defined in class,
    # but not upon instantiation
    with pytest.raises(ValueError):
        new_rule = NewRule(code="L000", description="")


def test_rules_configs_are_dynamically_documented():
    """Ensure that rule configurations are added to the class docstring."""
    @document_configuration
    class NewRule(BaseCrawler):
        """A new rule."""
        config_keywords = ["comma_style", "only_aliases"]

    assert "comma_style" in NewRule.__doc__
    assert "only_aliases" in NewRule.__doc__
