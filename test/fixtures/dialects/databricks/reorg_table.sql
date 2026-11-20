-- REORG TABLE. https://docs.databricks.com/aws/en/sql/language-manual/delta-reorg-table
REORG TABLE events APPLY (PURGE);

REORG TABLE events WHERE date >= '2022-01-01' APPLY (PURGE);

REORG events APPLY (CHECKPOINT);

REORG TABLE events APPLY (UPGRADE UNIFORM (ICEBERG_COMPAT_VERSION = 2));

REORG TABLE events APPLY (SET PARQUET (FORMAT_VERSION = '2.12.0'));
