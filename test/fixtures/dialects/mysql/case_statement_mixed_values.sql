-- Both servers accept these: a WHEN takes any expression in either form.
-- The simple form compares i with (i > 2); the searched form tests 2.
CREATE PROCEDURE p1(i INT)
BEGIN
    DECLARE a INT;
    CASE i
        WHEN 1 THEN SET a = 1;
        WHEN i > 2 THEN SET a = 2;
    END CASE;
    CASE
        WHEN i > 1 THEN SET a = 1;
        WHEN 2 THEN SET a = 2;
    END CASE;
END
