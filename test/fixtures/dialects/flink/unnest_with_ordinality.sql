SELECT
    order_id,
    product_name,
    product_index
FROM orders
CROSS JOIN UNNEST(product_names) WITH ORDINALITY AS t (product_name, product_index);

SELECT *
FROM (VALUES ('order_1'), ('order_2'))
CROSS JOIN UNNEST(ARRAY['shirt', 'pants', 'hat']) WITH ORDINALITY AS t (product_name, idx);

SELECT *
FROM (VALUES ('order_1'))
CROSS JOIN UNNEST(MAP['shirt', 2, 'pants', 1]) WITH ORDINALITY;
