-- get_query_results_as_dict() verifies SQLFluff can successfully use dbt_utils
-- functions that require a database connection.
-- https://github.com/sqlfluff/sqlfluff/issues/2297

with

orders as (
    select *
    from "postgres"."jaffle_shop"."orders"
)

select
    a,
    b,
    c,
    count(*) as occurences
from orders
group by 1,2,3
