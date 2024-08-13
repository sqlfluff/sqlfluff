-- define WITH clause
WITH revenue ( vkey, total_revenue ) AS (
      SELECT vendor_key, SUM(total_order_cost)
      FROM store.store_orders_fact
      GROUP BY vendor_key ORDER BY 1)
-- End WITH clause

-- primary query
SELECT v.vendor_name, v.vendor_address, v.vendor_city, r.total_revenue
FROM vendor_dimension v JOIN revenue r ON v.vendor_key = r.vkey
WHERE r.total_revenue = (SELECT MAX(total_revenue) FROM revenue )
ORDER BY vendor_name;

WITH
-- query sale amounts for each region
   regional_sales (region, total_sales) AS (
        SELECT sd.store_region, SUM(of.total_order_cost) AS total_sales
        FROM store.store_dimension sd JOIN store.store_orders_fact of ON sd.store_key = of.store_key
        GROUP BY store_region ),
-- query previous result set
   top_regions AS (
        SELECT region, total_sales
        FROM regional_sales ORDER BY total_sales DESC LIMIT 3
     )

-- primary query
-- aggregate sales in top_regions result set
SELECT sd.store_region AS region, pd.department_description AS department, SUM(of.total_order_cost) AS product_sales
FROM store.store_orders_fact of
JOIN store.store_dimension sd ON sd.store_key = of.store_key
JOIN public.product_dimension pd ON of.product_key = pd.product_key
WHERE sd.store_region IN (SELECT region FROM top_regions)
GROUP BY ROLLUP (region, department) ORDER BY region, product_sales DESC, GROUPING_ID();

INSERT INTO total_store_sales
WITH store_sales AS (
        SELECT sd.store_key, sd.store_region::VARCHAR(20), SUM (of.total_order_cost)
        FROM store.store_dimension sd JOIN store.store_orders_fact of ON sd.store_key = of.store_key
        GROUP BY sd.store_region, sd.store_key ORDER BY sd.store_region, sd.store_key)
SELECT * FROM store_sales;

WITH RECURSIVE nums (n) AS (
   SELECT 1 -- non-recursive (base) term
   UNION ALL
     SELECT n+1 FROM nums -- recursive term
  )
SELECT n FROM nums; -- primary query
