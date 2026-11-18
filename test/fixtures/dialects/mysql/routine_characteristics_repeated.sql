-- Valid on both servers, which keep the last value, but almost certainly a
-- mistake. Accepted because the server accepts it; flagging it is a job for
-- a rule.
CREATE FUNCTION f1(a INT) RETURNS INT
COMMENT 'first'
NO SQL
COMMENT 'second'
    RETURN a;

CREATE PROCEDURE p1()
NOT DETERMINISTIC
CONTAINS SQL
DETERMINISTIC
SQL SECURITY INVOKER
SQL SECURITY DEFINER
    SELECT 1;
