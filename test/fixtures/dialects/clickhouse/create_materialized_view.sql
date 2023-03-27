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
