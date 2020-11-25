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
