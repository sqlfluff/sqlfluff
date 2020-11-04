"""Tests for the standard set of rules."""

import pytest

from sqlfluff.core import Linter, FluffConfig
from sqlfluff.core.rules.base import BaseCrawler, LintResult, LintFix
from sqlfluff.core.rules.std import std_rule_set


def get_rule_from_set(code, config):
    """Fetch a rule from the rule set."""
    for r in std_rule_set.get_rulelist(config=config):
        if r.code == code:
            return r
    raise ValueError("{0!r} not in {1!r}".format(code, std_rule_set))


def assert_rule_fail_in_sql(code, sql, configs=None):
    """Assert that a given rule does fail on the given sql."""
    # Set up the config to only use the rule we are testing.
    cfg = FluffConfig(configs=configs, overrides={"rules": code})
    # Lint it using the current config (while in fix mode)
    linted = Linter(config=cfg).lint_string(sql, fix=True)
    lerrs = linted.get_violations()
    print("Errors Found: {0}".format(lerrs))
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
    parsed, _, _ = Linter(config=cfg).parse_string(sql)
    print("Parsed:\n {0}".format(parsed.stringify()))
    lerrs, _, _, _ = r.crawl(parsed, dialect=cfg.get("dialect_obj"), fix=True)
    print("Errors Found: {0}".format(lerrs))
    if any(v.rule.code == code for v in lerrs):
        pytest.fail(
            "Found {0} failures in query which should pass.".format(code), pytrace=False
        )


# ############## STD RULES TESTS
@pytest.mark.parametrize(
    "rule,pass_fail,qry,fixed,configs",
    [
        ("L001", "fail", "SELECT 1     \n", "SELECT 1\n", None),
        ("L002", "fail", "    \t    \t    SELECT 1", None, None),
        ("L003", "fail", "     SELECT 1", "SELECT 1", None),
        ("L004", "pass", "   \nSELECT 1", None, None),
        ("L004", "pass", "\t\tSELECT 1\n", None, None),
        ("L004", "fail", "   \n  \t \n  SELECT 1", None, None),
        ("L005", "fail", "SELECT 1 ,4", "SELECT 1,4", None),
        ("L008", "pass", "SELECT 1, 4", None, None),
        ("L008", "fail", "SELECT 1,   4", "SELECT 1, 4", None),
        ("L008", "fail", "SELECT 1,4", "SELECT 1, 4", None),
        ("L013", "pass", "SELECT *, foo from blah", None, None),
        ("L013", "fail", "SELECT upper(foo), bar from blah", None, None),
        ("L013", "pass", "SELECT *, foo from blah", None, None),
        # Don't expect alias if allow_scalar = True (default)
        ("L013", "pass", "SELECT 1 from blah", None, None),
        # Expect alias if allow_scalar = False
        (
            "L013",
            "fail",
            "SELECT 1 from blah",
            None,
            {"rules": {"allow_scalar": False}},
        ),
        ("L013", "pass", "SELECT upper(foo) as foo_up, bar from blah", None, None),
        ("L014", "pass", "SELECT a, b", None, None),
        ("L014", "pass", "SELECT A, B", None, None),
        # Check we get fails for using DISTINCT apparently incorrectly
        ("L015", "fail", "SELECT DISTINCT(a)", None, None),
        ("L015", "fail", "SELECT DISTINCT(a + b) * c", None, None),
        # Space after DISTINCT makes it okay...
        ("L015", "pass", "SELECT DISTINCT (a)", None, None),  # A bit iffy...
        ("L015", "pass", "SELECT DISTINCT (a + b) * c", None, None),  # Definitely okay
        # Test that fixes are consistent
        ("L014", "fail", "SELECT a,   B", "SELECT a,   b", None),
        ("L014", "fail", "SELECT B,   a", "SELECT B,   A", None),
        # Test that NULL is classed as a keyword and not an identifier
        ("L014", "pass", "SELECT NULL,   a", None, None),
        ("L010", "fail", "SELECT null,   a", "SELECT NULL,   a", None),
        # Test that we don't fail * operators in brackets
        ("L006", "pass", "SELECT COUNT(*) FROM tbl\n", None, None),
        # Long lines (with config override)
        (
            "L016",
            "pass",
            "SELECT COUNT(*) FROM tbl\n",
            None,
            {"rules": {"max_line_length": 30}},
        ),
        # Check we move comments correctly
        (
            "L016",
            "fail",
            "SELECT 1 -- Some Comment\n",
            "-- Some Comment\nSELECT 1\n",
            {"rules": {"max_line_length": 18}},
        ),
        # Check long lines that are only comments are linted correctly
        (
            "L016",
            "fail",
            "-- Some really long comments on their own line\nSELECT 1",
            None,
            {"rules": {"max_line_length": 18}},
        ),
        # Check we can add newlines after dedents (with an indent)
        (
            "L016",
            "fail",
            "    SELECT COUNT(*) FROM tbl\n",
            "    SELECT\n        COUNT(*)\n    FROM tbl\n",
            {"rules": {"max_line_length": 20}},
        ),
        # Check we handle indents nicely
        (
            "L016",
            "fail",
            "SELECT 12345\n",
            "SELECT\n    12345\n",
            {"rules": {"max_line_length": 10}},
        ),
        # Check priority of fixes
        (
            "L016",
            "fail",
            "SELECT COUNT(*) FROM tbl -- Some Comment\n",
            "-- Some Comment\nSELECT\n    COUNT(*)\nFROM tbl\n",
            {"rules": {"max_line_length": 18}},
        ),
        # Test that we don't have the "inconsistent" bug
        ("L010", "fail", "SeLeCt 1", "SELECT 1", None),
        ("L010", "fail", "SeLeCt 1 from blah", "SELECT 1 FROM blah", None),
        # Github Bug #99. Python2 Issues with fixing L003
        ("L003", "fail", "  select 1 from tbl;", "select 1 from tbl;", None),
        # Github Bug #207
        (
            "L006",
            "pass",
            "select\n    field,\n    date(field_1) - date(field_2) as diff\nfrom table",
            None,
            None,
        ),
        # Github Bug #203
        (
            "L003",
            "pass",
            "SELECT\n    -- Compute the thing\n    (a + b) AS c\nFROM\n    acceptable_buckets",
            None,
            None,
        ),
        (
            "L003",
            "pass",
            (
                "SELECT\n    user_id\nFROM\n    age_data\nJOIN\n    audience_size\n    USING (user_id, list_id)\n"
                "-- We LEFT JOIN because blah\nLEFT JOIN\n    verts\n    USING\n        (user_id)"
            ),
            None,
            None,
        ),
        # Leading commas
        (
            "L019",
            "fail",
            "SELECT\n    a\n    , b\n    FROM c",
            None,
            {"rules": {"L019": {"comma_style": "trailing"}}},
        ),
        (
            "L019",
            "pass",
            "SELECT\n    a\n    , b\n    FROM c",
            None,
            {"rules": {"L019": {"comma_style": "leading"}}},
        ),
        # Leading commas in with statement
        (
            "L019",
            "fail",
            (
                "WITH cte_1 as (\n    SELECT *\n    FROM table_1\n)\n\n"
                ", cte_2 as (\n    SELECT *\n    FROM table_2\n)\n\n"
                "SELECT * FROM table_3"
            ),
            None,
            {"rules": {"L019": {"comma_style": "trailing"}}},
        ),
        (
            "L019",
            "pass",
            (
                "WITH cte_1 as (\n    SELECT *\n    FROM table_1\n)\n\n"
                ", cte_2 as (\n    SELECT *\n    FROM table_2\n)\n\n"
                "SELECT * FROM table_3"
            ),
            None,
            {"rules": {"L019": {"comma_style": "leading"}}},
        ),
        # Trailing commas
        (
            "L019",
            "fail",
            "SELECT\n    a,\n    b\n    FROM c",
            None,
            {"rules": {"L019": {"comma_style": "leading"}}},
        ),
        (
            "L019",
            "pass",
            "SELECT\n    a,\n    b\n    FROM c",
            None,
            {"rules": {"L019": {"comma_style": "trailing"}}},
        ),
        # Using tabs as indents works
        (
            "L003",
            "fail",
            "SELECT\n\ta,\nb\nFROM my_tbl",
            "SELECT\n\ta,\n\tb\nFROM my_tbl",
            {"rules": {"indent_unit": "tab"}},
        ),
        # Configurable indents work.
        # a) default
        (
            "L003",
            "pass",
            "SELECT a, b, c\nFROM my_tbl\nLEFT JOIN another_tbl USING(a)",
            None,
            None,
        ),
        # b) specific
        (
            "L003",
            "pass",
            "SELECT a, b, c\nFROM my_tbl\nLEFT JOIN another_tbl USING(a)",
            None,
            {"indentation": {"indented_joins": False}},
        ),
        # c) specific True, but passing
        (
            "L003",
            "pass",
            "SELECT a, b, c\nFROM my_tbl\n    LEFT JOIN another_tbl USING(a)",
            None,
            {"indentation": {"indented_joins": True}},
        ),
        # d) specific True, but failing
        (
            "L003",
            "fail",
            "SELECT a, b, c\nFROM my_tbl\nLEFT JOIN another_tbl USING(a)",
            "SELECT a, b, c\nFROM my_tbl\n    LEFT JOIN another_tbl USING(a)",
            {"indentation": {"indented_joins": True}},
        ),
        # e) specific False, and failing
        (
            "L003",
            "fail",
            "SELECT a, b, c\nFROM my_tbl\n    LEFT JOIN another_tbl USING(a)",
            "SELECT a, b, c\nFROM my_tbl\nLEFT JOIN another_tbl USING(a)",
            {"indentation": {"indented_joins": False}},
        ),
        # Check fixing of single space rules
        (
            "L023",
            "fail",
            "WITH a AS(select 1) select * from a",
            "WITH a AS (select 1) select * from a",
            None,
        ),
        (
            "L024",
            "fail",
            "select * from a JOIN b USING(x)",
            "select * from a JOIN b USING (x)",
            None,
        ),
        # Check L024 passes if there's a newline between
        ("L024", "pass", "select * from a JOIN b USING\n(x)", None, None),
        # References in quotes in biquery
        (
            "L026",
            "pass",
            "SELECT bar.user_id FROM `foo.far.bar`",
            None,
            {"core": {"dialect": "bigquery"}},
        ),
        (
            "L026",
            "fail",
            "SELECT foo.user_id FROM `foo.far.bar`",
            None,
            {"core": {"dialect": "bigquery"}},
        ),
        # Mixed qualification of references.
        ("L028", "fail", "SELECT my_tbl.bar, baz FROM my_tbl", None, None),
        ("L028", "pass", "SELECT bar FROM my_tbl", None, None),
        ("L028", "pass", "SELECT my_tbl.bar FROM my_tbl", None, None),
        (
            "L028",
            "fail",
            "SELECT my_tbl.bar FROM my_tbl",
            None,
            {"rules": {"L028": {"single_table_references": "unqualified"}}},
        ),
        (
            "L028",
            "fail",
            "SELECT bar FROM my_tbl",
            None,
            {"rules": {"L028": {"single_table_references": "qualified"}}},
        ),
        # References in WHERE clause
        ("L026", "fail", "SELECT * FROM my_tbl WHERE foo.bar > 0", None, None),
        # Aliases not referenced.
        ("L025", "fail", "SELECT * FROM my_tbl AS foo", None, None),
        (
            "L025",
            "pass",
            "SELECT * FROM my_tbl AS foo JOIN other_tbl on other_tbl.x = foo.x",
            None,
            None,
        ),
        # Test cases for L029
        ("L029", "pass", "CREATE TABLE artist(artist_name TEXT)", None, None),
        ("L029", "fail", "CREATE TABLE artist(create TEXT)", None, None),
        ("L029", "fail", "SELECT 1 as parameter", None, None),
        (
            "L029",
            "pass",
            "SELECT parameter",
            None,
            None,
        ),  # should pass on default config as not alias
        (
            "L029",
            "fail",
            "SELECT parameter",
            None,
            {"rules": {"L029": {"only_aliases": False}}},
        ),
        # Inconsistent capitalisation of functions
        (
            "L030",
            "fail",
            "SELECT MAX(id), min(id) from table",
            "SELECT MAX(id), MIN(id) from table",
            None,
        ),
        (
            "L030",
            "fail",
            "SELECT MAX(id), min(id) from table",
            "SELECT max(id), min(id) from table",
            {"rules": {"L030": {"capitalisation_policy": "lower"}}},
        ),
        # Check we don't get false alarms with newlines, or sign indicators.
        ("L006", "pass", "SELECT 1\n+ 2", None, None),
        ("L006", "pass", "SELECT 1\n\t+ 2", None, None),
        ("L006", "pass", "SELECT 1\n    + 2", None, None),
        ("L006", "pass", "SELECT 1, +2, -4", None, None),
        # Catch issues with subqueries properly
        (
            "L028",
            "pass",
            "SELECT * FROM db.sc.tbl2\nWHERE a NOT IN (SELECT a FROM db.sc.tbl1)\n",
            None,
            None,
        ),
        (
            "L026",
            "pass",
            "SELECT * FROM db.sc.tbl2\nWHERE a NOT IN (SELECT a FROM db.sc.tbl1)\n",
            None,
            None,
        ),
        (
            "L026",
            "pass",
            "SELECT * FROM db.sc.tbl2\nWHERE a NOT IN (SELECT tbl2.a FROM db.sc.tbl1)\n",
            None,
            None,
        ),  # Correlated subquery.
        # Make sure comments are aligned properly
        (
            "L003",
            "pass",
            "SELECT *\nFROM\n    t1\n-- Comment\nJOIN t2 USING (user_id)",
            None,
            None,
        ),
        (
            "L003",
            "fail",
            "SELECT *\nFROM\n    t1\n    -- Comment\nJOIN t2 USING (user_id)",
            "SELECT *\nFROM\n    t1\n-- Comment\nJOIN t2 USING (user_id)",
            None,
        ),
        # L013 & L025 Fixes with https://github.com/sqlfluff/sqlfluff/issues/449
        (
            "L013",
            "pass",
            "select ps.*, pandgs.blah from ps join pandgs using(moo)",
            None,
            None,
        ),
        (
            "L025",
            "pass",
            "select ps.*, pandgs.blah from ps join pandgs using(moo)",
            None,
            None,
        ),
        # L031 Allow self-joins
        (
            "L031",
            "pass",
            "select x.a, x_2.b from x left join x as x_2 on x.foreign_key = x.foreign_key",
            None,
            None,
        ),
        # L031 fixes issues
        (
            "L031",
            "fail",
            "SELECT u.id, c.first_name, c.last_name, COUNT(o.user_id) FROM users as u JOIN customers as c on u.id = c.user_id JOIN orders as o on u.id = o.user_id;",
            "SELECT users.id, customers.first_name, customers.last_name, COUNT(orders.user_id) FROM users JOIN customers on users.id = customers.user_id JOIN orders on users.id = orders.user_id;",
            None,
        ),
        # Fix for https://github.com/sqlfluff/sqlfluff/issues/476
        (
            "L010",
            "fail",
            "SELECT * FROM MOO ORDER BY dt DESC",
            "select * from MOO order by dt desc",
            {"rules": {"L010": {"capitalisation_policy": "lower"}}},
        ),
        # Test for capitalise casing
        (
            "L010",
            "fail",
            "SELECT * FROM MOO ORDER BY dt DESC",
            "Select * From MOO Order By dt Desc",
            {"rules": {"L010": {"capitalisation_policy": "capitalise"}}},
        ),
        ("L032", "pass", "select x.a from x inner join y on x.id = y.id", None, None),
        ("L032", "fail", "select x.a from x inner join y using (id)", None, None),
        (
            "L032",
            "fail",
            "select x.a from x inner join y on x.id = y.id inner join z using (id)",
            None,
            None,
        ),
        # Test cases for L022, both leading and trailing commas.
        (
            "L022",
            "pass",
            "with my_cte as (\n    select 1\n),\n\nother_cte as (\n    select 1\n)\n\nselect * from my_cte cross join other_cte",
            None,
            None,
        ),
        (
            "L022",
            "pass",
            "with my_cte as (\n    select 1\n)\n\n, other_cte as (\n    select 1\n)\n\nselect * from my_cte cross join other_cte",
            None,
            None,
        ),
        (
            "L022",
            "fail",
            "with my_cte as (\n    select 1\n),\nother_cte as (\n    select 1\n)\n\nselect * from my_cte cross join other_cte",
            "with my_cte as (\n    select 1\n),\n\nother_cte as (\n    select 1\n)\n\nselect * from my_cte cross join other_cte",
            None,
        ),
        (
            "L022",
            "fail",
            "with my_cte as (\n    select 1\n),\n-- Comment\nother_cte as (\n    select 1\n)\n\nselect * from my_cte cross join other_cte",
            "with my_cte as (\n    select 1\n),\n\n-- Comment\nother_cte as (\n    select 1\n)\n\nselect * from my_cte cross join other_cte",
            None,
        ),
        (
            "L022",
            "fail",
            "with my_cte as (\n    select 1\n),\n\nother_cte as (\n    select 1\n)\nselect * from my_cte cross join other_cte",
            "with my_cte as (\n    select 1\n),\n\nother_cte as (\n    select 1\n)\n\nselect * from my_cte cross join other_cte",
            None,
        ),
        (
            "L022",
            "fail",
            "with my_cte as (\n    select 1\n)\n, other_cte as (\n    select 1\n)\nselect * from my_cte cross join other_cte",
            "with my_cte as (\n    select 1\n)\n\n, other_cte as (\n    select 1\n)\n\nselect * from my_cte cross join other_cte",
            None,
        ),
        # Fixes oneline cte with leading comma style
        (
            "L022",
            "fail",
            "with my_cte as (select 1), other_cte as (select 1) select * from my_cte cross join other_cte",
            "with my_cte as (select 1)\n\n, other_cte as (select 1)\n\nselect * from my_cte cross join other_cte",
            {"rules": {"comma_style": "leading"}},
        ),
        # Fixes cte with a floating comma
        (
            "L022",
            "fail",
            "with my_cte as (select 1)\n,\nother_cte as (select 1)\nselect * from my_cte cross join other_cte",
            "with my_cte as (select 1)\n,\nother_cte as (select 1)\n\nselect * from my_cte cross join other_cte",
            None,
        ),
        # Bare UNION without a DISTINCT or ALL
        (
            "L033",
            "pass",
            "SELECT a, b FROM tbl UNION ALL SELECT c, d FROM tbl1",
            None,
            None,
        ),
        (
            "L033",
            "fail",
            "SELECT a, b FROM tbl UNION SELECT c, d FROM tbl1",
            None,
            None,
        ),
        (
            "L033",
            "fail",
            "SELECT a, b FROM tbl\n UNION\nSELECT c, d FROM tbl1",
            None,
            None,
        ),
        (
            "L033",
            "pass",
            "SELECT a, b FROM tbl\nUNION DISTINCT\nSELECT c, d FROM tbl1",
            None,
            None,
        ),
        (
            "L033",
            "pass",
            "SELECT a, b FROM tbl\n--selecting a and b\nUNION DISTINCT\nSELECT c, d FROM tbl1",
            None,
            None,
        ),
        (
            "L033",
            "fail",
            "SELECT a, b FROM tbl UNION DISTINCT SELECT c, d\nFROM tbl1 UNION SELECT e, f FROM tbl2",
            None,
            None,
        ),
        ("L034", "pass", "select a, cast(b as int) as b, c from x", None, None),
        (
            "L034",
            "fail",
            "select a, row_number() over (partition by id order by date) as y, b from x",
            "select a, b, row_number() over (partition by id order by date) as y from x",
            None,
        ),
        (
            "L034",
            "fail",
            "select row_number() over (partition by id order by date) as y, *, cast(b as int) as b_int from x",
            "select *, cast(b as int) as b_int, row_number() over (partition by id order by date) as y from x",
            None,
        ),
        (
            "L034",
            "fail",
            "select row_number() over (partition by id order by date) as y, cast(b as int) as b_int, * from x",
            "select *, cast(b as int) as b_int, row_number() over (partition by id order by date) as y from x",
            None,
        ),
        (
            "L034",
            "fail",
            "select row_number() over (partition by id order by date) as y, b::int, * from x",
            "select *, b::int, row_number() over (partition by id order by date) as y from x",
            None,
        ),
        (
            "L034",
            "fail",
            "select row_number() over (partition by id order by date) as y, *, 2::int + 4 as sum, cast(b) as c from x",
            "select *, cast(b) as c, row_number() over (partition by id order by date) as y, 2::int + 4 as sum from x",
            None,
        ),
        (
            "L033",
            "fail",
            "select a, b from tbl union distinct select c, d\nfrom tbl1 union select e, f from tbl2",
            None,
            None,
        ),
        # with statement indentation
        (
            "L018",
            "pass",
            "with cte as (\n    select 1\n) select * from cte",
            None,
            None,
        ),
        # with statement oneline
        (
            "L018",
            "pass",
            "with cte as (select 1) select * from cte",
            None,
            None,
        ),
        # Fix with statement indentation
        (
            "L018",
            "fail",
            "with cte as (\n    select 1\n    ) select * from cte",
            "with cte as (\n    select 1\n) select * from cte",
            None,
        ),
        # Fix with statement that has negative indentation
        (
            "L018",
            "fail",
            "    with cte as (\n    select 1\n) select * from cte",
            "    with cte as (\n    select 1\n    ) select * from cte",
            None,
        ),
        # still runs with unparsable with statement
        ("L018", "pass", "with (select 1)", None, None),
        # duplicate aliases
        (
            "L020",
            "fail",
            "select 1 from table_1 as a join table_2 as a using(pk)",
            None,
            None,
        ),
        # check if using select distinct and group by
        ("L021", "pass", "select a from b group by a", None, None),
        ("L021", "fail", "select distinct a from b group by a", None, None),
        # Add whitespace when fixing implicit aliasing
        (
            "L011",
            "fail",
            "select foo.bar from (select 1 as bar)foo",
            "select foo.bar from (select 1 as bar) AS foo",
            None,
        ),
    ],
)
def test__rules__std_string(rule, pass_fail, qry, fixed, configs):
    """Test that a rule passes/fails on a given string.

    Optionally, also test the fixed string if provided.
    """
    if pass_fail == "fail":
        res = assert_rule_fail_in_sql(rule, qry, configs=configs)
        # If a `fixed` value is provided then check it matches
        if fixed:
            assert res == fixed
    elif pass_fail == "pass":
        assert_rule_pass_in_sql(rule, qry, configs=configs)
    else:
        raise ValueError(
            "Test setup fail: Unexpected value for pass_fail: {0!r}".format(pass_fail)
        )


class Rule_T042(BaseCrawler):
    """A dummy rule."""

    def _eval(self, segment, raw_stack, **kwargs):
        pass


class Rule_T001(BaseCrawler):
    """A deliberately malicious rule."""

    def _eval(self, segment, raw_stack, **kwargs):
        """Stars make newlines."""
        if segment.is_type("star"):
            return LintResult(
                anchor=segment,
                fixes=[
                    LintFix("create", segment, self.make_newline(segment.pos_marker))
                ],
            )


def test__rules__user_rules():
    """Test that can safely add user rules."""
    # Set up a linter with the user rule
    linter = Linter(user_rules=[Rule_T042])
    # Make sure the new one is in there.
    assert ("T042", "A dummy rule.") in linter.rule_tuples()
    # Instantiate a second linter and check it's NOT in there.
    # This tests that copying and isolation works.
    linter = Linter()
    assert not any(rule[0] == "T042" for rule in linter.rule_tuples())


def test__rules__runaway_fail_catch():
    """Test that we catch runaway rules."""
    runaway_limit = 5
    my_query = "SELECT * FROM foo"
    # Set up the config to only use the rule we are testing.
    cfg = FluffConfig(overrides={"rules": "T001", "runaway_limit": runaway_limit})
    # Lint it using the current config (while in fix mode)
    linter = Linter(config=cfg, user_rules=[Rule_T001])
    # In theory this step should result in an infinite
    # loop, but the loop limit should catch it.
    linted = linter.lint_string(my_query, fix=True)
    # We should have a lot of newlines in there.
    # The number should equal the runaway limit
    assert linted.tree.raw.count("\n") == runaway_limit


@pytest.mark.parametrize(
    "rule,path,violations",
    [
        ("L001", "test/fixtures/linter/indentation_errors.sql", [(4, 24)]),
        ("L002", "test/fixtures/linter/indentation_errors.sql", [(3, 1), (4, 1)]),
        (
            "L003",
            "test/fixtures/linter/indentation_errors.sql",
            [(2, 4), (3, 4), (4, 6)],
        ),
        (
            "L004",
            "test/fixtures/linter/indentation_errors.sql",
            [(3, 1), (4, 1), (5, 1)],
        ),
        # Check we get comma (with leading space/newline) whitespace errors
        # NB The newline before the comma, should report on the comma, not the newline for clarity.
        ("L005", "test/fixtures/linter/whitespace_errors.sql", [(2, 9)]),
        ("L019", "test/fixtures/linter/whitespace_errors.sql", [(4, 1)]),
        # Check we get comma (with incorrect trailing space) whitespace errors,
        # but also no false positives on line 4 or 5.
        ("L008", "test/fixtures/linter/whitespace_errors.sql", [(3, 12)]),
        # Check we get operator whitespace errors and it works with brackets
        (
            "L006",
            "test/fixtures/linter/operator_errors.sql",
            [(3, 8), (4, 10), (7, 6), (7, 7), (7, 9), (7, 10), (7, 12), (7, 13)],
        ),
        ("L007", "test/fixtures/linter/operator_errors.sql", [(5, 9)]),
        # Check we DO get a violation on line 2 but NOT on line 3
        (
            "L006",
            "test/fixtures/linter/operator_errors_negative.sql",
            [(2, 6), (2, 9), (5, 6), (5, 7)],
        ),
        # Hard indentation errors
        (
            "L003",
            "test/fixtures/linter/indentation_error_hard.sql",
            [(2, 4), (6, 5), (9, 13), (14, 14), (19, 5), (20, 6)],
        ),
        # Check bracket handling with closing brackets and contained indents works.
        ("L003", "test/fixtures/linter/indentation_error_contained.sql", []),
        # Check we handle block comments as expect. Github #236
        (
            "L016",
            "test/fixtures/linter/block_comment_errors.sql",
            [(1, 121), (2, 99), (4, 88)],
        ),
        ("L016", "test/fixtures/linter/block_comment_errors_2.sql", [(1, 85), (2, 86)]),
        # Column references
        ("L027", "test/fixtures/linter/column_references.sql", [(1, 8)]),
        ("L027", "test/fixtures/linter/column_references_bare_function.sql", []),
        ("L026", "test/fixtures/linter/column_references.sql", [(1, 11)]),
        ("L025", "test/fixtures/linter/column_references.sql", [(2, 11)]),
        # Distinct and Group by
        ("L021", "test/fixtures/linter/select_distinct_group_by.sql", [(1, 8)]),
        # Make sure that ignoring works as expected
        ("L006", "test/fixtures/linter/operator_errors_ignore.sql", [(10, 8), (10, 9)]),
        ("L031", "test/fixtures/linter/aliases_in_join_error.sql", [(6, 15), (7, 19), (8, 16)]),
    ],
)
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
    r = get_rule_from_set("L003", config=cfg)
    test_stack = generate_test_segments(["bar", "\n", "     ", "foo", "baar", " \t "])
    res = r._process_raw_stack(test_stack)
    print(res)
    assert sorted(res.keys()) == [1, 2]
    assert res[2]["indent_size"] == 5


@pytest.mark.parametrize(
    "rule_config_dict",
    [
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
    ],
)
def test_improper_configs_are_rejected(rule_config_dict):
    """Ensure that unsupported configs raise a ValueError."""
    config = FluffConfig(configs={"rules": rule_config_dict})
    with pytest.raises(ValueError):
        std_rule_set.get_rulelist(config)


def test_rules_cannot_be_instantiated_without_declared_configs():
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

    @std_rule_set.document_configuration
    class RuleWithConfig(BaseCrawler):
        """A new rule with configuration."""

        config_keywords = ["comma_style", "only_aliases"]

    assert "comma_style" in RuleWithConfig.__doc__
    assert "only_aliases" in RuleWithConfig.__doc__

    @std_rule_set.document_configuration
    class RuleWithoutConfig(BaseCrawler):
        """A new rule without configuration."""

        pass

    assert "Configuration" not in RuleWithoutConfig.__doc__
