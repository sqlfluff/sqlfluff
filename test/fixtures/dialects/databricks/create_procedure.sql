-- CREATE PROCEDURE. https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-procedure
CREATE OR REPLACE PROCEDURE add(x INT, y INT, OUT sum INT, INOUT total INT)
LANGUAGE SQL SQL SECURITY INVOKER COMMENT 'Add two numbers'
AS
BEGIN
    SET sum = x + y;
    SET total = total + sum;
END;

CREATE PROCEDURE greeting(IN mode STRING)
LANGUAGE SQL
AS
BEGIN
    SELECT 1;
END;
