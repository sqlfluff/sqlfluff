with

orders as (
    select *
    from "jaffle_shop"."jaffle_shop"."orders"
)

select
    a,
    b,
    c,
    count(*) as occurences
from orders
group by 1,2,3
