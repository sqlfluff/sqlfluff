select * from (
    select times_purchased, state_code
    from customers t
)
pivot
(
    count(state_code)
    for state_code in ('NY' as new_york,'CT','NJ','FL','MO')
);

select * from (
    select times_purchased, state_code
    from customers t
)
pivot
(
    count(state_code)
    for state_code in (select distinct state_code from state)
);

select * from (
    select times_purchased, state_code
    from customers t
)
pivot
(
    count(state_code)
    for state_code in (any)
);

select *
from   sale_stats
unpivot
(
    quantity
    for product_code
    in (
        product_a AS 'A',
        product_b AS 'B',
        product_c AS 'C'
    )
);

select *
from   sale_stats
unpivot include nulls
(
    quantity
    for product_code
    in (
        product_a AS 'A',
        product_b AS 'B',
        product_c AS 'C'
    )
);

select *
from   sale_stats
unpivot
(
    (quantity, amount)
    for product_code
    in (
        (a_qty, a_value) as 'A',
        (b_qty, b_value) as 'B'
    )
);

select * from (
    select times_purchased, state_code
    from customers t
)
pivot
(
    count(state_code) as state_code
    for state_code in (any)
);
