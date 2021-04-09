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