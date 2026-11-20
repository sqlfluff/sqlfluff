-- REFRESH FOREIGN. https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-refresh-foreign
REFRESH FOREIGN CATALOG c;

REFRESH FOREIGN SCHEMA c.s;

REFRESH FOREIGN TABLE c.s.t RESOLVE DBFS LOCATION;
