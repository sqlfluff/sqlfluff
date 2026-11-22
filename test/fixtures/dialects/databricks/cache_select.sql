-- CACHE SELECT. https://docs.databricks.com/aws/en/sql/language-manual/delta-cache
CACHE SELECT * FROM boxes;

CACHE SELECT width, length FROM boxes WHERE height = 3;
