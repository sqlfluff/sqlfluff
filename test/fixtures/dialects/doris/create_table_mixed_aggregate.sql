CREATE TABLE mixed_aggregate_test
(
    user_id INT,
    username STRING,
    age INT,
    score DECIMAL(5, 2) MAX,
    last_login DATETIME,
    login_count INT SUM,
    user_tags STRING REPLACE,
    is_active BOOLEAN
)
AGGREGATE KEY (user_id, username)
DISTRIBUTED BY HASH (user_id)
PROPERTIES (
    'replication_num' = '1'
); 