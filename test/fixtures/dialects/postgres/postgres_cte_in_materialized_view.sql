CREATE MATERIALIZED VIEW public.mv_sales
TABLESPACE pg_default
AS

WITH regional_sales AS (
    SELECT
        region,
        SUM(amount) AS total_sales
    FROM orders
    GROUP BY region
),

top_regions AS (
    SELECT region
    FROM regional_sales
    WHERE total_sales > (SELECT SUM(total_sales) / 10 FROM regional_sales)
)

SELECT
    region,
    product,
    SUM(quantity) AS product_units,
    SUM(amount) AS product_sales
FROM orders
WHERE region IN (SELECT region FROM top_regions)
GROUP BY region, product
WITH DATA;
