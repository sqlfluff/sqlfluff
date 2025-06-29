CREATE TABLE bitmap_hll_test
(
    user_id INT,
    page_views BITMAP BITMAP_UNION,
    unique_visitors HLL HLL_UNION,
    session_duration QUANTILE QUANTILE_UNION,
    page_id INT,
    visit_time DATETIME,
    user_agent STRING REPLACE
)
AGGREGATE KEY (user_id, page_id)
DISTRIBUTED BY HASH (user_id)
PROPERTIES (
    'replication_num' = '1'
); 

