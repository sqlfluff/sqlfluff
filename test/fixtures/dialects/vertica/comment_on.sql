-- This test file includes all examples from the Vertica docs,
-- but not all are implemented so some are commented out for now.
-- See https://docs.vertica.com/latest/en/sql-reference/statements/comment-on-statements/

COMMENT ON AGGREGATE FUNCTION APPROXIMATE_MEDIAN(x FLOAT) IS 'alias of APPROXIMATE_PERCENTILE with 0.5 as its parameter';
COMMENT ON AGGREGATE FUNCTION APPROXIMATE_MEDIAN(x FLOAT) IS NULL;

COMMENT ON ANALYTIC FUNCTION an_rank() IS 'built from the AnalyticFunctions library';
COMMENT ON ANALYTIC FUNCTION an_rank() IS NULL;

COMMENT ON CONSTRAINT constraint_x ON promotion_dimension IS 'Primary key';
COMMENT ON CONSTRAINT constraint_x ON promotion_dimension IS NULL;

COMMENT ON FUNCTION macros.zerowhennull(x INT) IS 'Returns a 0 if not NULL';
COMMENT ON FUNCTION macros.zerowhennull(x INT) IS NULL;

COMMENT ON LIBRARY MyFunctions IS 'In development';
COMMENT ON LIBRARY MyFunctions IS NULL;

COMMENT ON NODE initiator IS 'Initiator node';
COMMENT ON NODE initiator IS NULL;

COMMENT ON PROJECTION customer_dimension_vmart_node01 IS 'Test data';
COMMENT ON PROJECTION customer_dimension_vmart_node01 IS NULL;

COMMENT ON COLUMN customer_dimension_vmart_node01.customer_name IS 'Last name only';
COMMENT ON COLUMN customer_dimension_vmart_node01.customer_name IS NULL;

COMMENT ON SCHEMA public  IS 'All users can access this schema';
COMMENT ON SCHEMA public IS NULL;

COMMENT ON SEQUENCE prom_seq IS 'Promotion codes';
COMMENT ON SEQUENCE prom_seq IS NULL;

COMMENT ON TABLE promotion_dimension IS '2011 Promotions';
COMMENT ON TABLE promotion_dimension IS NULL;

COMMENT ON COLUMN store.store_sales_fact.transaction_time IS 'GMT';
COMMENT ON COLUMN store.store_sales_fact.transaction_time IS NULL;

COMMENT ON TRANSFORM FUNCTION macros.zerowhennull(x INT) IS 'Returns a 0 if not NULL';
COMMENT ON TRANSFORM FUNCTION macros.zerowhennull(x INT) IS NULL;

COMMENT ON VIEW curr_month_ship IS 'Shipping data for the current month';
COMMENT ON VIEW curr_month_ship IS NULL;
