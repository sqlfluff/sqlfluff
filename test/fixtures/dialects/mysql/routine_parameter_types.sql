-- A parameter or return type may carry a character set and a collation.
CREATE PROCEDURE p1(
    IN a VARCHAR(10) CHARACTER SET utf8mb4,
    OUT b TEXT CHARSET latin1 COLLATE latin1_bin,
    c CHAR(3) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin
)
    SELECT a, c;

CREATE FUNCTION f1(a VARCHAR(255) CHARACTER SET utf8mb4)
RETURNS VARCHAR(255) CHARACTER SET utf8mb4
    RETURN a;

-- Database-qualified routine names (db_name.sp_name).
CREATE PROCEDURE zz.p2() SELECT 1;
CREATE FUNCTION `zz`.`f2`(a INT UNSIGNED) RETURNS DECIMAL(10, 2) RETURN a;

-- Local variables take the same type.
CREATE PROCEDURE p3()
BEGIN
    DECLARE a CHAR CHARACTER SET utf8mb4;
    DECLARE b VARCHAR(5) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT 'x';
    SELECT a, b;
END;
