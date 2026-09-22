-- OFFSET clause. https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-qry-select-offset
SELECT * FROM t OFFSET 3;

SELECT * FROM t ORDER BY a LIMIT ALL OFFSET 0;

SELECT * FROM t ORDER BY a OFFSET length('SPARK');
