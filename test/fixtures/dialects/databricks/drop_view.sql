-- DROP MATERIALIZED VIEW is documented alongside DROP VIEW:
-- https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-drop-view
DROP MATERIALIZED VIEW employeeview;

-- The MATERIALIZED keyword is optional, and IF EXISTS still applies to both.
DROP MATERIALIZED VIEW IF EXISTS employeeview;

DROP VIEW employeeview;

DROP VIEW IF EXISTS employeeview;

-- Qualified names take the same shape.
DROP MATERIALIZED VIEW usersc.employeeview;
