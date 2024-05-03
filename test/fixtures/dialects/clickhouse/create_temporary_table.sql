CREATE TEMPORARY TABLE xt0 AS SELECT * FROM x;
CREATE TEMPORARY TABLE IF NOT EXISTS t2
(
    ty String,
    t2 String,
    c_date_time DateTime32
)
ENGINE = MergeTree
ORDER BY (ty,t2)
TTL c_date_time + INTERVAL  1 DAY
