-- get_query_results_as_dict() verifies SQLFluff can successfully use dbt_utils
-- functions that require a database connection.
-- https://github.com/sqlfluff/sqlfluff/issues/2297
{% set saved_var = dbt_utils.get_query_results_as_dict(
    "SELECT schema_name
FROM information_schema.schemata"
    )
%}
with

orders as (
    select *
    from {{ source("jaffle_shop", "orders") }}
)

select
    a,
    b,
    c,
    count(*) as occurences
from orders
{{ dbt_utils.group_by(3) }}
