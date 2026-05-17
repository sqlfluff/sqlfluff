CREATE TEMPORARY TABLE market_hours_source (
    `timestamp_utc` TIMESTAMP(3),
    `market` STRING,
    `market_open_flag` BOOLEAN
) WITH (
    'connector' = 'kafka',
    'topic' = 'data-ops-market-hours'
);

CREATE TEMPORARY TABLE market_hours_source (
    `timestamp_utc` TIMESTAMP(3),
    `market` STRING,
    `market_open_flag` BOOLEAN,
    proc_time AS PROCTIME()
) WITH (
    'connector' = 'kafka',
    'topic' = 'data-ops-market-hours'
);
