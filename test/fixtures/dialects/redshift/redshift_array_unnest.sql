WITH example_data AS (
    SELECT
        10 AS shop_id
        , json_parse('[1, 2]') AS inventory
    UNION ALL
    SELECT
        20 AS shop_id
        , json_parse('[3, 4, 5]') AS inventory
    UNION ALL
    SELECT
        30 AS shop_id
        , json_parse('[6, 7, 8, 9]') AS inventory
)

SELECT
    shop_id
    , value
    , index
FROM example_data ed, ed.inventory AS value AT index;

SELECT c_name, orders.o_orderkey AS orderkey, index AS orderkey_index
FROM customer_orders_lineitem c, c.c_orders AS orders AT index
ORDER BY orderkey_index;

-- can extract the correlated values from multiple arrays using the index variable
SELECT
    value_a::BIGINT,
    array_b[idx]::VARCHAR AS value_b,
    array_c[MOD(idx, 3) + 1]::FLOAT8 AS value_c
FROM mytable t, t.array_a AS value_a AT idx;
