CREATE PROCEDURE p1(i INT)
BEGIN
    DECLARE a INT;
    CASE i
        WHEN 1 THEN SET a = 1;
        WHEN 2 THEN SET a = 2;
        ELSE SET a = 0;
    END CASE;
    CASE
        WHEN i > 0 THEN SET a = 1;
        WHEN i < 0 THEN SET a = -1;
    END CASE;
END;

-- MariaDB also accepts a CASE statement outside a stored program.
CASE
    WHEN 1 = 1 THEN SELECT 1;
    ELSE SELECT 2;
END CASE;
