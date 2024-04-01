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
