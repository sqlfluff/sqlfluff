-- FOR, WHILE, LOOP and REPEAT statements.
-- https://docs.databricks.com/aws/en/sql/language-manual/control-flow/for-stmt
-- https://docs.databricks.com/aws/en/sql/language-manual/control-flow/while-stmt
-- https://docs.databricks.com/aws/en/sql/language-manual/control-flow/loop-stmt
-- https://docs.databricks.com/aws/en/sql/language-manual/control-flow/repeat-stmt
BEGIN
    DECLARE sum INT DEFAULT 0;
    FOR row AS
        SELECT num FROM range(1, 20) AS t(num)
    DO
        SET sum = sum + row.num;
    END FOR;
    VALUES (sum);
END;

BEGIN
    DECLARE num INT DEFAULT 0;
    sumNumbers: LOOP
        SET num = num + 1;
        IF num > 10 THEN
            LEAVE sumNumbers;
        END IF;
        IF num % 2 = 0 THEN
            ITERATE sumNumbers;
        END IF;
    END LOOP sumNumbers;
END;

BEGIN
    DECLARE num INT DEFAULT 0;
    sumNumbers: WHILE num < 10 DO
        SET num = num + 1;
    END WHILE sumNumbers;
END;

BEGIN
    DECLARE num INT DEFAULT 0;
    sumNumbers: REPEAT
        SET num = num + 1;
    UNTIL num = 10
    END REPEAT sumNumbers;
END;
