CREATE TABLE foodb.events ON CLUSTER '{cluster}' (
        timestamp DateTime,
        mt_id UInt32,
        event VARCHAR,
        uuid UUID,
        value Int32
)
ENGINE = ReplicatedMergeTree('/clickhouse/{cluster}/databases/{database}/all/tables/{table}', '{replica}')
ORDER BY (mt_id, toStartOfDay(timestamp), event, uuid)
SETTINGS index_granularity = 8192;
