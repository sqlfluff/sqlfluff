-- REFRESH (MATERIALIZED VIEW / STREAMING TABLE / TABLE / FUNCTION).
-- https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-refresh-full
REFRESH MATERIALIZED VIEW v;

REFRESH STREAMING TABLE t WHERE x > 1;

REFRESH TABLE t FULL;

REFRESH t;

REFRESH FUNCTION s.f;
