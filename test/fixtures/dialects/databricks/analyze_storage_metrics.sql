-- ANALYZE TABLE ... COMPUTE STORAGE METRICS.
-- https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-analyze-compute-storage-metrics
ANALYZE TABLE t COMPUTE STORAGE METRICS;

ANALYZE TABLE t COMPUTE STORAGE METRICS USING INVENTORY LOCATION 's3://b/p/' CONF 'cfg';
