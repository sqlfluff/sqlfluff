CREATE PROCEDURE p1(i INT)
BEGIN
    DECLARE a INT;
    CASE
        WHEN i > 0 THEN SET a = 1;
        WHEN i < 0 THEN
            SET a = -1;
            WHILE a < 0 DO
                SET a = a + 1;
            END WHILE;
            BEGIN
                SET a = 2;
            END;
        WHEN i IS NULL OR a IS NULL THEN SET a = 3;
        ELSE SET a = 0;
    END CASE;
    CASE
        WHEN i = 1 THEN SET a = 1;
        WHEN i = 2 THEN SET a = 2;
        WHEN i = 3 THEN SET a = 3;
    END CASE;
END
