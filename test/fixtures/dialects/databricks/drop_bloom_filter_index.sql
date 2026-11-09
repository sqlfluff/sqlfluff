-- DROP BLOOMFILTER INDEX. https://docs.databricks.com/aws/en/sql/language-manual/delta-drop-bloomfilter-index
DROP BLOOMFILTER INDEX ON TABLE t;

DROP BLOOMFILTER INDEX ON t FOR COLUMNS (a, b);
