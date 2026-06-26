select * from (
    select
        times_purchased,
        state_code
    from customers
) purchases
pivot
(
    count(state_code)
    for state_code in ('NY' as new_york, 'CT', 'NJ', 'FL', 'MO')
);

select * from (
    select
        times_purchased,
        state_code
    from customers
) purchases
pivot
(
    count(state_code)
    for state_code in (select distinct state_code from state)
);

select * from (
    select
        times_purchased,
        state_code
    from customers
) purchases
pivot
(
    count(state_code)
    for state_code in (select distinct state_code from state)
)
where
    state_code in ('NY', 'CT', 'NJ', 'FL', 'MO');

select * from (
    select
        times_purchased,
        state_code
    from customers
) purchases
pivot
(
    count(state_code)
    for state_code in (any)
);

select * from (
    select
        times_purchased,
        state_code
    from customers
) purchases
pivot
(
    count(state_code) as state_code
    for state_code in (any)
);


select
    quantity,
    product_code
from sale_stats
unpivot
(
    quantity
    for product_code
    in (
        product_a as 'A',
        product_b as 'B',
        product_c as 'C'
    )
);

select
    quantity,
    product_code
from sale_stats
unpivot
(
    quantity
    for product_code
    in (
        product_a as 'A',
        product_b as 'B',
        product_c as 'C'
    )
)
where
    quantity > 0;

select
    quantity,
    product_code
from sale_stats
unpivot include nulls
(
    quantity
    for product_code
    in (
        product_a as 'A',
        product_b as 'B',
        product_c as 'C'
    )
);

select
    quantity,
    product_id
from sale_stats
unpivot
(
    quantity
    for product_id
    in (
        product_a as 1,
        product_b as 2,
        product_c as 3
    )
);

select
    quantity,
    amount
from sale_stats
unpivot
(
    quantity, amount
    for product_code
    in (
        a_qty, a_value as 'A',
        b_qty, b_value as 'B'
    )
);

select
    quantity,
    amount
from sale_stats
unpivot
(
    quantity, amount
    for product_code
    in (
        a_qty, a_value as 1,
        b_qty, b_value as 2
    )
);

select
    quantity,
    product_code
from sale_stats
unpivot
(
    quantity
    for product_code
    in (product_a, product_b, product_c)
);

select
    quantity,
    amount,
    product_code
from sale_stats
unpivot
(
    quantity, amount
    for product_code
    in (
        (a_qty, a_value),
        (b_qty, b_value)
    )
);
