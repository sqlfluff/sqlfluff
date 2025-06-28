CREATE TABLE simple_aggregate_test
(
    id INT,
    name STRING,
    count INT SUM,
    value INT MAX
)
AGGREGATE KEY (id)
DISTRIBUTED BY HASH (id)
PROPERTIES (
    'replication_num' = '1'
); 