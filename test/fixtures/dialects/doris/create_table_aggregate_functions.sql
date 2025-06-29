CREATE TABLE aggregate_functions_test
(
    id INT,
    value1 INT MAX,
    value2 INT MIN,
    value3 STRING REPLACE,
    value4 DECIMAL(10, 2) SUM,
    value5 BITMAP BITMAP_UNION,
    value6 HLL HLL_UNION,
    value7 QUANTILE QUANTILE_UNION
)
AGGREGATE KEY (id)
DISTRIBUTED BY HASH (id)
PROPERTIES (
    'replication_num' = '1'
); 

