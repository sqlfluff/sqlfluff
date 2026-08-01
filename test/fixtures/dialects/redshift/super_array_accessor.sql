-- Navigating into a SUPER column in the FROM clause, where the path
-- indexes into an array part way through.
-- https://docs.aws.amazon.com/redshift/latest/dg/query-super.html
SELECT raw_data.resource_id
FROM raw_data
LEFT JOIN raw_data.topic[0].extension AS topic_extension_array ON TRUE;

SELECT c.c_name
FROM customer_orders_lineitem AS c, c.c_orders[0] AS o;

SELECT t.id
FROM mytable AS t
LEFT JOIN t.array_a[0].array_b[1] AS nested ON TRUE;
