-- A parameter may have a default value, used when the caller leaves it out.
-- A default may refer to an earlier parameter.
CREATE PROCEDURE p1(IN a INT DEFAULT 5, b INT DEFAULT a + 1)
    SELECT a, b;

CREATE FUNCTION f1(a INT DEFAULT 10) RETURNS INT
    RETURN a * 2;

CREATE FUNCTION f2(
    a VARCHAR(10) CHARACTER SET utf8mb4 DEFAULT 'x',
    b INT DEFAULT NULL
) RETURNS VARCHAR(20)
    RETURN CONCAT(a, COALESCE(b, 0));
