CREATE MATERIALIZED VIEW IF NOT EXISTS db.table_mv
TO db.table
AS
    SELECT
        column1,
        column2
    FROM db.table_kafka;

CREATE MATERIALIZED VIEW table_mv
TO table
AS
    SELECT
        column1,
        column2
    FROM table_kafka;

CREATE MATERIALIZED VIEW IF NOT EXISTS db.table_mv
ON CLUSTER mycluster
TO db.table
AS
    SELECT
        column1,
        column2
    FROM db.table_kafka;

CREATE MATERIALIZED VIEW table_mv
TO table
ENGINE = MergeTree()
AS
    SELECT
        column1,
        column2
    FROM table_kafka;

CREATE MATERIALIZED VIEW table_mv
ENGINE = MergeTree()
AS
    SELECT
        column1,
        column2
    FROM table_kafka;

CREATE MATERIALIZED VIEW table_mv
ENGINE = MergeTree()
POPULATE
AS
    SELECT
        column1,
        column2
    FROM table_kafka;

CREATE MATERIALIZED VIEW db.mv_table
ENGINE MergeTree
ORDER BY ()
AS SELECT * FROM db.table;

-- Basic materialized view
CREATE MATERIALIZED VIEW my_view
ENGINE = MergeTree()
ORDER BY id
AS SELECT id, name FROM source_table;

-- Materialized view with IF NOT EXISTS
CREATE MATERIALIZED VIEW IF NOT EXISTS my_view_2
ENGINE = MergeTree()
ORDER BY id
AS SELECT id, value FROM source_table;

-- Materialized view with ON CLUSTER (explicit cluster name)
CREATE MATERIALIZED VIEW my_view_3
ON CLUSTER my_cluster
ENGINE = MergeTree()
ORDER BY id
AS SELECT id, timestamp FROM source_table;

-- Materialized view with ON CLUSTER (using cluster macro)
CREATE MATERIALIZED VIEW my_view_3_macro
ON CLUSTER '{cluster}'
ENGINE = MergeTree()
ORDER BY id
AS SELECT id, timestamp FROM source_table;

-- Materialized view with TO clause
CREATE MATERIALIZED VIEW my_view_4
TO target_table
AS SELECT id, category FROM source_table;

-- Materialized view with IF NOT EXISTS, ON CLUSTER, and TO clause
CREATE MATERIALIZED VIEW IF NOT EXISTS cdc_lay.table_mv
ON CLUSTER default
TO stg_lay.table
AS SELECT * FROM source_table;

-- Materialized view with IF NOT EXISTS, ON CLUSTER macro, and TO clause
CREATE MATERIALIZED VIEW IF NOT EXISTS cdc_lay.table_mv_macro
ON CLUSTER '{cluster}'
TO stg_lay.table
AS SELECT * FROM source_table;

-- Materialized view with IF NOT EXISTS, ON CLUSTER macro, and TO clause
CREATE MATERIALIZED VIEW IF NOT EXISTS cdc_lay.table_mv_macro
ON CLUSTER default
TO stg_lay.table
AS SELECT * FROM source_table;

-- Materialized view with POPULATE
CREATE MATERIALIZED VIEW my_view_5
ENGINE = MergeTree()
ORDER BY id
POPULATE
AS SELECT id, status FROM source_table;

-- Materialized view with complex engine settings
CREATE MATERIALIZED VIEW my_view_6
ENGINE = ReplicatedReplacingMergeTree('/clickhouse/tables/{shard}/my_view_6', '{replica}')
PARTITION BY toYYYYMM(timestamp)
ORDER BY (id, timestamp)
TTL timestamp + INTERVAL 1 MONTH
SETTINGS index_granularity = 8192
AS SELECT id, timestamp, value FROM source_table;


-- Materialized view with TO and database.table syntax
CREATE MATERIALIZED VIEW my_view_7
ON CLUSTER '{cluster}'
TO db.target_table
AS SELECT * FROM source_table;

-- Materialized view with complex SELECT query
CREATE MATERIALIZED VIEW my_view_8
ENGINE = SummingMergeTree()
ORDER BY (category, metric)
AS
SELECT
    category,
    metric,
    sum(value) AS total_value,
    count() AS count,
    avg(value) AS avg_value
FROM source_table
GROUP BY category, metric;

-- Materialized view with IF NOT EXISTS, ON CLUSTER, TO clause with column list
CREATE MATERIALIZED VIEW IF NOT EXISTS cdc_lay.table_mv2
ON CLUSTER default
TO stg_lay.table2 (id, name, value)
AS SELECT id, name, value FROM source_table;

-- Materialized view from kafka table with column list
CREATE MATERIALIZED VIEW IF NOT EXISTS db.consumer_kafka
ON CLUSTER '{cluster}'
TO db.local AS
SELECT *, _timestamp_ms AS processedAt
FROM db.kafka;

-- Materialized view with ARRAY JOIN
CREATE MATERIALIZED VIEW IF NOT EXISTS db.nested_data_mv
ON CLUSTER '{cluster}'
TO db.nested_data_local AS
SELECT
    identifier,
    _timestamp_ms AS processedAt,
    metrics.measuredAt AS measuredAt,
    metrics.value AS value,
    metrics.name AS name
FROM db.kafka
ARRAY JOIN metrics;

-- Materialized view with subquery in FROM clause and GROUP BY
CREATE MATERIALIZED VIEW IF NOT EXISTS db.aggeregating_mv
ON CLUSTER '{cluster}'
TO db.aggeregating_local AS
SELECT
    identifier,
    _ingestedAt AS ingestedAt,
    objectList
FROM
(
    SELECT
        toStartOfDay(ingestedAt) AS _ingestedAt,
        identifier,
        groupUniqArray(objectIdentfier) AS objectList
    FROM db.raw_table
    GROUP BY
        identifier,
        _ingestedAt
);

-- Materialized view with subquery in FROM clause and GROUP BY
CREATE MATERIALIZED VIEW IF NOT EXISTS db.aggeregating_mv2
ON CLUSTER '{cluster}'
TO db.aggeregating_local2 AS
SELECT
    identifier,
    _ingestedAt AS ingestedAt,
    valueCount,
    cumulativeLagSeconds
FROM (
    SELECT
        identifier,
        toStartOfMinute(ingestedAt) AS _ingestedAt,
        count() AS valueCount,
        sum((toUnixTimestamp64Milli(ingestedAt) - toUnixTimestamp64Milli(measuredAt)) / 1000) AS cumulativeLagSeconds
    FROM db.raw_table
    GROUP BY identifier, _ingestedAt
);

-- Materialized view with TO clause and complex SELECT
CREATE MATERIALIZED VIEW IF NOT EXISTS db.kafka_errors
ON CLUSTER '{cluster}'
TO db.kafka_errors_local AS
SELECT
    _topic AS topic,
    _partition AS kafka_partition,
    _offset AS offset,
    ifNull(_timestamp_ms, now()) AS processedAt,
    _raw_message AS raw_message,
    _error AS error
FROM db.kafka
WHERE length(_error) > 0;
