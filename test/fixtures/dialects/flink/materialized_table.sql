CREATE MATERIALIZED TABLE my_materialized_table (
    PRIMARY KEY (id) NOT ENFORCED
)
PARTITIONED BY (dt)
WITH (
    'connector' = 'paimon'
)
FRESHNESS = INTERVAL '3' HOUR
REFRESH_MODE = FULL
AS
SELECT
    id,
    dt,
    amount
FROM source_orders;

CREATE OR ALTER MATERIALIZED TABLE my_streaming_mt (
    id BIGINT,
    ts TIMESTAMP(3),
    WATERMARK FOR ts AS ts - INTERVAL '5' SECOND,
    PRIMARY KEY (id) NOT ENFORCED
)
DISTRIBUTED BY HASH (id) INTO 4 BUCKETS
WITH (
    'connector' = 'paimon'
)
START_MODE = FROM_BEGINNING
FRESHNESS = INTERVAL '1' MINUTE
REFRESH_MODE = CONTINUOUS
AS
SELECT
    id,
    ts
FROM source_events;

CREATE MATERIALIZED TABLE mt_from_now
START_MODE = FROM_NOW(INTERVAL '1' HOUR)
AS
SELECT *
FROM source_events;

CREATE MATERIALIZED TABLE mt_from_ts
START_MODE = FROM_TIMESTAMP(TIMESTAMP '2026-01-01 00:00:00')
AS
SELECT *
FROM source_events;

CREATE MATERIALIZED TABLE mt_minimal
AS
SELECT *
FROM source_events;

ALTER MATERIALIZED TABLE my_materialized_table SUSPEND;

ALTER MATERIALIZED TABLE my_materialized_table RESUME WITH ('sink.parallelism' = '4');

ALTER MATERIALIZED TABLE my_materialized_table REFRESH PARTITION (dt = '2026-01-01');

ALTER MATERIALIZED TABLE my_materialized_table SET FRESHNESS = INTERVAL '5' MINUTE;

ALTER MATERIALIZED TABLE my_materialized_table SET REFRESH_MODE = CONTINUOUS;

ALTER MATERIALIZED TABLE my_materialized_table SET ('sink.parallelism' = '8');

ALTER MATERIALIZED TABLE my_materialized_table RESET ('sink.parallelism');

ALTER MATERIALIZED TABLE my_materialized_table RENAME TO my_materialized_table_v2;

ALTER MATERIALIZED TABLE my_materialized_table_v2
START_MODE = RESUME_OR_FROM_NOW(INTERVAL '10' MINUTE)
AS
SELECT
    id,
    dt
FROM source_orders;

ALTER MATERIALIZED TABLE my_materialized_table_v2 ADD (
    extra STRING COMMENT 'extra field' AFTER id,
    WATERMARK FOR ts AS ts - INTERVAL '5' SECOND
);

ALTER MATERIALIZED TABLE my_materialized_table_v2 MODIFY DISTRIBUTION BY HASH (id) INTO 8 BUCKETS;

ALTER MATERIALIZED TABLE my_materialized_table_v2 DROP (extra, legacy_col);

DROP MATERIALIZED TABLE IF EXISTS my_materialized_table_v2;
