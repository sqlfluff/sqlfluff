"""Test the interactions of AL09, CP02 & RF06.

AL09: Self aliasing
CP02: Identifier Capitalisation
RF06: Identifier Quoting
"""

import pytest

import sqlfluff

input_query = """
select
    a as A,
    B as b,
    "C" as C,
    "d" as d,
    "E" as e,
    f as F,
    g as "G",
    h as h,
    I as I
from foo
"""


@pytest.mark.parametrize(
    "rules,dialect,fixed_sql",
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
    f as F,
    g as "G",
    h,
    I
from foo
""",
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
    f as f,
    g as "G",
    h as h,
    i as i
from foo
""",
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
    f as F,
    g as G,
    h as h,
    I as I
from foo
""",
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
    f,
    g as "G",
    h,
    i
from foo
""",
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
    f as F,
    g as G,
    h,
    I
from foo
""",
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
    f as f,
    g as g,
    h as h,
    i as i
from foo
""",
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
    f,
    g,
    h,
    i
from foo
""",
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
        ),
        # Ditto Trino (and also MySQL, but it has different identifier
        # quoting so would need a more complex test case).
        (
            ["AL09", "CP02", "RF06"],
            "trino",
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
        ),
    ],
)
def test__rules__std_AL09_CP02_RF06(rules, dialect, fixed_sql):
    """Test interactions between AL09, CP02 & RF06."""
    print(f"Running with rules: {rules}")
    result = sqlfluff.fix(input_query, dialect=dialect, rules=rules)
    assert result == fixed_sql
