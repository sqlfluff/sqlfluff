-- SYNC. https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-sync
SYNC TABLE main.default.t FROM hive_metastore.default.t;

SYNC SCHEMA main.s AS EXTERNAL FROM hive_metastore.s;

SYNC TABLE main.default.t FROM hive_metastore.default.t SET OWNER `u` DRY RUN;
