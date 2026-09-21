-- FSCK REPAIR TABLE. https://docs.databricks.com/aws/en/sql/language-manual/delta-fsck
FSCK REPAIR TABLE t;

FSCK REPAIR TABLE t METADATA ONLY DRY RUN;

FSCK REPAIR TABLE t VERIFY ALL FILES;

FSCK REPAIR TABLE t VERIFY FILES MODIFIED BETWEEN current_timestamp() AND current_timestamp();
