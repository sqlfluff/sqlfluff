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
