WITH example_data AS (
    SELECT
        10 AS shop_id
        , json_parse('{"apple_count": 2, "orange_count": 6}') AS inventory
    UNION ALL
    SELECT
        20 AS shop_id
        , json_parse('{"pear_count": 10, "other_data": 42}') AS inventory
    UNION ALL
    SELECT
        30 AS shop_id
        , json_parse('{"apple_count": 3, "lemon_count": 5}') AS inventory
)

SELECT
    shop_id
    , key
    , value
FROM example_data ed, UNPIVOT ed.inventory AS value AT key;

SELECT attr as attribute_name, val as object_value
FROM customer_orders_lineitem c, c.c_orders AS o, UNPIVOT o AS val AT attr
WHERE c_custkey = 9451;
