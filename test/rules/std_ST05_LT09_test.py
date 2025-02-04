"""Tests observed conflict between ST05 & LT09."""

from sqlfluff.core import FluffConfig, Linter


def test__rules__std_ST05_LT09_4137() -> None:
    """Tests observed conflict between ST05 & LT09.

    In this case, the moved `t2` table was created after the first usage.
    https://github.com/sqlfluff/sqlfluff/issues/4137
    """
    sql = """
with

cte1 as (
    select t1.x, t2.y
    from tbl1 t1
    join (select x, y from tbl2) t2
        on t1.x = t2.x
)

, cte2 as (
    select x, y from tbl2 t2
)

select x, y from cte1
union all
select x, y from cte2
;
"""
    fixed_sql = """
with t2 as (select
x,
y
from tbl2),
cte1 as (
    select
t1.x,
t2.y
    from tbl1 t1
    join t2
        on t1.x = t2.x
),
cte2 as (
    select
x,
y
from tbl2 t2
)
select
x,
y
from cte1
union all
select
x,
y
from cte2
;
"""
    cfg = FluffConfig.from_kwargs(
        dialect="ansi",
        rules=["ST05", "LT09"],
    )
    result = Linter(config=cfg).lint_string(sql, fix=True)
    assert result.fix_string()[0] == fixed_sql


def test__rules__std_ST05_LT09_5265() -> None:
    """Tests observed conflict between ST05 & LT09.

    In this case, the moved `t2` table was created after the first usage.
    https://github.com/sqlfluff/sqlfluff/issues/4137
    """
    sql = """
with

cte1 as (
    select t1.x, t2.y
    from tbl1 t1
    join (select x, y from tbl2) t2
        on t1.x = t2.x
)

, cte2 as (
    select x, y from tbl2 t2
)

select x, y from cte1
union all
select x, y from cte2
;
"""
    fixed_sql = """
with t2 as (select
x,
y
from tbl2),
cte1 as (
    select
t1.x,
t2.y
    from tbl1 t1
    join t2
        on t1.x = t2.x
),
cte2 as (
    select
x,
y
from tbl2 t2
)
select
x,
y
from cte1
union all
select
x,
y
from cte2
;
"""
    cfg = FluffConfig.from_kwargs(
        dialect="ansi",
        rules=["ST05", "LT09"],
    )
    result = Linter(config=cfg).lint_string(sql, fix=True)
    assert result.fix_string()[0] == fixed_sql
