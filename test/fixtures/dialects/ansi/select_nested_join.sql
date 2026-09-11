-- query with no brackets
select
    orders.order_id AS order_id,
    customers.email AS email
from
    orders
    join customers on(
        (
            customers.customer_id = orders.customer_id
        )
    )
where
    (customers.email = 'sample@gmail.com')
group by
    orders.order_id,
    customers.email
order by
    orders.order_id;

-- nested bracketed up to 1 levels
select
    orders.order_id AS order_id,
    customers.email AS email
from
    (
        orders
        join customers on(
            (
                customers.customer_id = orders.customer_id
            )
        )
    )
where
    (customers.email = 'sample@gmail.com')
group by
    orders.order_id,
    customers.email
order by
    orders.order_id;

-- nested bracketed up to 2 levels
select
    orders.order_id AS order_id,
    customers.email AS email
from
    (
        (
            orders
            join customers on(
                (
                    customers.customer_id = orders.customer_id
                )
            )
        )
        join products on(
            (products.product_id = orders.product_id)
        )
    )
where
    (customers.email = 'sample@gmail.com')
group by
    orders.order_id,
    customers.email
order by
    orders.order_id;

-- nested bracketed up to 3 levels
select
    orders.order_id AS order_id,
    customers.email AS email
from
    (
        (
            (
                orders
                join customers on(
                    (
                        customers.customer_id = orders.customer_id
                    )
                )
            )
            join products on(
                (products.product_id = orders.product_id)
            )
        )
        join random on(
            (random.product_id = products.product_id)
        )
    )
where
    (customers.email = 'sample@gmail.com')
group by
    orders.order_id,
    customers.email
order by
    orders.order_id;

-- redundant brackets around a join used as a join target
-- https://github.com/sqlfluff/sqlfluff/issues/8382
select 1
from a
left join ((b inner join c on true)) on true;

-- three redundant layers, to pin that the depth is not capped
select 1
from a
left join (((b inner join c on true))) on true;

-- a join after the inner bracket
select 1
from a
left join ((b inner join c on true) left join d on true) on true;

-- redundant brackets in the FROM clause, which parsed before #8382 and must
-- keep the tree they had
select 1
from (((a inner join b on true)));

-- four layers
select 1
from a
left join ((((b inner join c on true)))) on true;

-- the alias inside the brackets is still the join target's alias
select a.x
from tbl_a as a
inner join ((tbl_b as b inner join tbl_c as c on b.id = c.id)) on a.id = b.id;

-- join forms other than LEFT ... ON
select 1
from a
cross join ((b inner join c on true));

select 1
from a
natural join ((b inner join c on true));

select 1
from a
left join ((b inner join c on true)) using (x);

select 1
from a
full outer join ((b inner join c on true)) on true;
