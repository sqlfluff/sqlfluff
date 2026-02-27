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

CREATE OR REPLACE VIEW IF NOT EXISTS db.view_mv_with_security
(
    column1_alias,
    column2_alias
)
ON CLUSTER mycluster
DEFINER = CURRENT_USER
SQL SECURITY INVOKER
AS SELECT
    column1,
    column2
FROM db.table_kafka
COMMENT 'View with definer and security';
