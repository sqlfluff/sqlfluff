-- The full header in the server's order:
-- CREATE [DEFINER = user] {FUNCTION | PROCEDURE} [IF NOT EXISTS] name ...
CREATE DEFINER = 'u'@'localhost' FUNCTION IF NOT EXISTS f1(a INT)
RETURNS INT
NO SQL
COMMENT 'header order'
    RETURN a;

CREATE DEFINER = CURRENT_USER PROCEDURE IF NOT EXISTS p1(IN a INT, OUT b INT)
READS SQL DATA
BEGIN
    SET b = a;
END;

-- A labelled block as the body, left early with LEAVE.
CREATE FUNCTION f2(a INT)
RETURNS INT
DETERMINISTIC
fbody: BEGIN
    IF a < 0 THEN
        LEAVE fbody;
    END IF;
    RETURN a;
END fbody;
