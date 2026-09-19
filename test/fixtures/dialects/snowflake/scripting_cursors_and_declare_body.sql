-- Snowflake Scripting cursors and DECLARE prefixed bodies
-- https://docs.snowflake.com/en/developer-guide/snowflake-scripting/cursors
-- https://docs.snowflake.com/en/sql-reference/sql/create-procedure
-- https://docs.snowflake.com/en/sql-reference/sql/create-task

DECLARE
    c1 CURSOR FOR SELECT price FROM invoices;
    total NUMBER := 0;
BEGIN
    OPEN c1;
    FETCH c1 INTO total;
    CLOSE c1;
    RETURN total;
END;

DECLARE
    c1 CURSOR FOR SELECT price, quantity FROM invoices;
    row_price NUMBER := 0;
    row_quantity NUMBER := 0;
BEGIN
    OPEN c1 USING (minimum_price, maximum_price);
    FETCH c1 INTO row_price, row_quantity;
    CLOSE c1;
    RETURN row_price;
END;

-- A procedure body may declare variables before its block
CREATE PROCEDURE p()
RETURNS INT
LANGUAGE SQL
AS
DECLARE
    x INT DEFAULT 1;
BEGIN
    RETURN x;
END;

CREATE OR REPLACE PROCEDURE p2()
RETURNS NUMBER
LANGUAGE SQL
AS
DECLARE
    c1 CURSOR FOR SELECT price FROM invoices;
    total NUMBER := 0;
BEGIN
    OPEN c1;
    FETCH c1 INTO total;
    CLOSE c1;
    RETURN total;
END;

-- So may a task body
CREATE TASK t1
WAREHOUSE = wh1
SCHEDULE = '5 MINUTES'
AS
DECLARE
    x INTEGER DEFAULT 1;
BEGIN
    INSERT INTO t VALUES (x);
END;
