CREATE VIEW db.view_mv
AS SELECT
    column1,
    column2
FROM db.table_kafka;

CREATE VIEW db.view_mv
ON CLUSTER mycluster
AS SELECT
    column1,
    column2
FROM db.table_kafka;

CREATE OR REPLACE VIEW db.view_mv
AS SELECT
    column1,
    column2
FROM db.table_kafka;

CREATE OR REPLACE VIEW db.view_mv
ON CLUSTER mycluster
AS SELECT
    column1,
    column2
FROM db.table_kafka;

CREATE VIEW IF NOT EXISTS db.view_mv
AS SELECT
    column1,
    column2
FROM db.table_kafka;

CREATE VIEW IF NOT EXISTS db.view_mv
AS SELECT
    column1,
    column2
FROM db.table_kafka;

CREATE VIEW IF NOT EXISTS db.view_mv
ON CLUSTER mycluster
AS SELECT
    column1,
    column2
FROM db.table_kafka;
