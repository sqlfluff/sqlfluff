-- redshift_super_data_type.sql
/* queries that implicitly and explicitly use the Redshift SUPER data type
(https://docs.aws.amazon.com/redshift/latest/dg/super-overview.html). */

-- Example from https://github.com/sqlfluff/sqlfluff/issues/1672
SELECT
    c[0].col,
    o
FROM customer_orders c, c.c_orders o;

-- Can use SUPER data types in WHERE clauses
SELECT COUNT(*)
FROM customer_orders_lineitem
WHERE c_orders[0].o_orderkey IS NOT NULL;

SELECT c_custkey
FROM customer_orders_lineitem
WHERE CASE WHEN JSON_TYPEOF(c_orders[0].o_orderstatus) = 'string'
           THEN c_orders[0].o_orderstatus::VARCHAR <= 'P'
      ELSE NULL END;

-- Can do multiple array accessors with SUPER data types
SELECT
    c[0][1][2][3][4].col,
    o
FROM customer_orders c, c.c_orders o;

-- Can use wildcards
SELECT
    c.*,
    o
FROM
    customer_orders_lineitem c,
    c.c_orders o;

-- Can access a single SUPER data type multiple times in a SELECT statement
-- source: https://awscloudfeed.com/whats-new/big-data/work-with-semistructured-data-using-amazon-redshift-super
SELECT
    messages[0].format,
    messages[0].topic
FROM
    subscription_auto
WHERE
    messages[0].payload.payload."assetId" > 0;

-- Can perform functions and operations on SUPER data types.
-- Adapted from: https://awscloudfeed.com/whats-new/big-data/work-with-semistructured-data-using-amazon-redshift-super
SELECT
    messages[0].format,
    COUNT(messages[0].topic)
FROM
    subscription_auto
WHERE
    messages[0].payload.payload."assetId" > 'abc'
GROUP BY
    messages[0].format;
