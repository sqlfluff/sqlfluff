-- REPAIR TABLE. https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-repair-table
REPAIR TABLE t;

MSCK REPAIR TABLE t SYNC METADATA;

REPAIR TABLE t ADD PARTITIONS;
