ALTER TABLE my_table ADD category_id STRING COMMENT 'identifier of the category';

ALTER TABLE IF EXISTS my_table ADD (
    log_ts STRING COMMENT 'log timestamp string' FIRST,
    ts AS TO_TIMESTAMP(log_ts) AFTER log_ts,
    meta_ts TIMESTAMP_LTZ(3) METADATA FROM 'timestamp' VIRTUAL AFTER ts,
    PRIMARY KEY (id) NOT ENFORCED,
    WATERMARK FOR ts AS ts - INTERVAL '3' SECOND
);

ALTER TABLE my_table ADD IF NOT EXISTS
PARTITION (p1 = 1, p2 = 'a') WITH ('k1' = 'v1')
PARTITION (p1 = 1, p2 = 'b') WITH ('k2' = 'v2');

ALTER TABLE my_table ADD DISTRIBUTION BY HASH (uid) INTO 4 BUCKETS;

ALTER TABLE my_table ADD DISTRIBUTION BY (uid);

ALTER TABLE my_table ADD DISTRIBUTION INTO 4 BUCKETS;

ALTER TABLE my_table MODIFY measurement DOUBLE COMMENT 'bytes per second' AFTER `id`;

ALTER TABLE my_table MODIFY (
    log_ts STRING COMMENT 'log timestamp string' AFTER `id`,
    ts AS TO_TIMESTAMP(log_ts) AFTER log_ts,
    PRIMARY KEY (id) NOT ENFORCED,
    WATERMARK FOR ts AS ts
);

ALTER TABLE my_table MODIFY DISTRIBUTION BY RANGE (uid) INTO 8 BUCKETS;

ALTER TABLE my_table DROP measurement;

ALTER TABLE my_table DROP (col1, col2, col3);

ALTER TABLE my_table DROP PRIMARY KEY;

ALTER TABLE my_table DROP CONSTRAINT pk_constraint;

ALTER TABLE my_table DROP IF EXISTS PARTITION (`id` = 1), PARTITION (`id` = 2);

ALTER TABLE my_table DROP WATERMARK;

ALTER TABLE my_table DROP DISTRIBUTION;

ALTER TABLE my_table RENAME request_body TO payload;

ALTER TABLE my_table RENAME TO my_table_v2;

ALTER TABLE datagen_source SET ('rows-per-second' = '10');

ALTER TABLE datagen_source RESET ('rows-per-second', 'number-of-rows');
