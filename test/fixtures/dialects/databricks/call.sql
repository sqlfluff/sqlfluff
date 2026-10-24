-- CALL. https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-call
CALL area_of_rectangle(5, 10, area, acc);

CALL area_of_rectangle(y => 10, x => 5, area => area, acc => acc);
