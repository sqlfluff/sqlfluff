select foo, count(*) from bar group by all;

select
    letter,
    sum(num) as sum_num
from
    table_test
group by grouping sets (1, ());

select
    letter,
    sum(num) as sum_num
from
    table_test
group by grouping sets (letter, ());

select
    product_type,
    product_name,
    sum(product_count) as product_sum
from products
group by
    grouping sets (
        product_type,
        rollup(product_type, product_name)
    )
order by product_type, product_name;

select
    product_type,
    product_name,
    sum(product_count) as product_sum
from products
group by
    grouping sets (
        product_type,
        cube(product_type, product_name)
    )
order by product_type, product_name;

select
    product_type,
    product_name,
    sum(product_count) as product_sum
from products
group by rollup (product_type, product_name)
order by product_type, product_name;

select
    product_type,
    product_name,
    sum(product_count) as product_sum
from products
group by cube (product_type, product_name)
order by product_type, product_name;
