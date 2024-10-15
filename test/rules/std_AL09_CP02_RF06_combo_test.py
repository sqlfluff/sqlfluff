"""Test the interactions of AL09, CP02 & RF06.

AL09: Self aliasing
CP02: Identifier Capitalisation
RF06: Identifier Quoting
"""

import pytest

from sqlfluff.core import Linter

input_query = """
select
    a as A,
    B as b,
    "C" as C,
    "d" as d,
    "E" as e,
    "f" as F,
    g as "G",
    h as h,
    I as I
from foo
"""


@pytest.mark.parametrize(
    "rules,dialect,fixed_sql,post_fix_errors",
    [
        # NOTE: The first few examples here are with ANSI which is
        # configured as a natively UPPERCASE dialect.
        (
            ["AL09"],
            "ansi",
            """
select
    a as A,
    B as b,
    "C" as C,
    "d" as d,
    "E" as e,
    "f" as F,
    g as "G",
    h,
    I
from foo
""",
            [
                # These two (A & B) are detected as self aliases, but not
                # auto-fixed, because the intent is ambiguous.
                # Should the alias/reference be quoted or removed?
                ("AL09", 3, 5),
                ("AL09", 4, 5),
            ],
        ),
        (
            ["CP02"],
            "ansi",
            """
select
    a as a,
    b as b,
    "C" as c,
    "d" as d,
    "E" as e,
    "f" as f,
    g as "G",
    h as h,
    i as i
from foo
""",
            [],
        ),
        (
            ["RF06"],
            "ansi",
            """
select
    a as A,
    B as b,
    C as C,
    "d" as d,
    E as e,
    "f" as F,
    g as G,
    h as h,
    I as I
from foo
""",
            [],
        ),
        (
            ["AL09", "CP02"],
            "ansi",
            """
select
    a,
    b,
    "C" as c,
    "d" as d,
    "E" as e,
    "f" as f,
    g as "G",
    h,
    i
from foo
""",
            # NOTE: When CP02 is active, AL09 errors are no longer
            # present, because CP02 allowed them to be resolved.
            [],
        ),
        (
            ["AL09", "RF06"],
            "ansi",
            """
select
    a as A,
    B as b,
    C,
    "d" as d,
    E as e,
    "f" as F,
    g as G,
    h,
    I
from foo
""",
            [
                # Without CPO2, the errors on line 3 & 5 are present. They're
                # detected as self-aliases, but with ambiguous fixes (A & B).
                ("AL09", 3, 5),
                ("AL09", 4, 5),
                # Additionally, with RF06 removing quotes, it creates two
                # new issues, where the previously quoted aliases are now
                # unquoted, but still different cases (E & G).
                ("AL09", 7, 5),
                ("AL09", 9, 5),
            ],
        ),
        (
            ["CP02", "RF06"],
            "ansi",
            """
select
    a as a,
    b as b,
    c as c,
    "d" as d,
    e as e,
    "f" as f,
    g as g,
    h as h,
    i as i
from foo
""",
            [],
        ),
        (
            ["AL09", "CP02", "RF06"],
            "ansi",
            """
select
    a,
    b,
    c,
    "d" as d,
    e,
    "f" as f,
    g,
    h,
    i
from foo
""",
            [],
        ),
        # Postgres is natively lowercase, and so the results are
        # different.
        (
            ["AL09", "CP02", "RF06"],
            "postgres",
            """
select
    a,
    b,
    "C" as c,
    d,
    "E" as e,
    f,
    g as "G",
    h,
    i
from foo
""",
            [],
        ),
        # DuckDB is always case insensitive so likewise has a different result.
        (
            ["AL09", "CP02", "RF06"],
            "duckdb",
            """
select
    a,
    b,
    c,
    d,
    e,
    f,
    g,
    h,
    i
from foo
""",
            [],
        ),
        # Clickhouse is always case sensitive has a more conservative result.
        # All the quotes are gone, but all the aliases with a case change remain.
        (
            # NOTE: Testing without CP02 as that rule is much less appropriate
            # for clickhouse.
            ["AL09", "RF06"],
            "clickhouse",
            """
select
    a as A,
    B as b,
    C,
    d,
    E as e,
    f as F,
    g as G,
    h,
    I
from foo
""",
            # None of those aliases should be flagged as an issue.
            [],
        ),
    ],
)
def test__rules__std_AL09_CP02_RF06(rules, dialect, fixed_sql, post_fix_errors):
    """Test interactions between AL09, CP02 & RF06."""
    print(f"Running with rules: {rules}")
    linter = Linter(dialect=dialect, rules=rules)
    result = linter.lint_string(input_query, fix=True)
    fixed, _ = result.fix_string()
    assert fixed == fixed_sql
    # Check violations after fix.
    # NOTE: We should really use the rules testing utilities here
    # but they don't yet support multiple rules.
    post_fix_result = linter.lint_string(fixed, fix=False)
    assert post_fix_result.check_tuples() == post_fix_errors
