-- Postgres style WITHIN GROUP window functions
SELECT ARRAY_AGG(o_orderkey) WITHIN GROUP (ORDER BY o_orderkey ASC)
FROM orders
