CREATE PROCEDURE p1(i INT)
BEGIN
    DECLARE a INT;
    CASE i
        WHEN 1 THEN SET a = 1;
        WHEN 2 THEN
            SET a = 2;
            IF a > 1 THEN
                SET a = 3;
            END IF;
            BEGIN
                SET a = 4;
            END;
        WHEN i + 1 THEN SET a = 5;
        ELSE SET a = 0;
    END CASE;
    CASE i + 1
        WHEN 1 THEN SET a = 1;
        WHEN 2 THEN SET a = 2;
        WHEN 3 THEN SET a = 3;
    END CASE;
END
