-- BEGIN ... END compound statement and declarations.
-- https://docs.databricks.com/aws/en/sql/language-manual/control-flow/compound-stmt
BEGIN ATOMIC
    INSERT INTO accounts VALUES (1, 'Alice', 1000);
    UPDATE accounts SET balance = balance + 100 WHERE id = 1;
END;

BEGIN
    DECLARE a INT DEFAULT 1;
    DECLARE b, c STRING;
    DECLARE my_error CONDITION FOR SQLSTATE '45000';
    DECLARE EXIT HANDLER FOR DIVIDE_BY_ZERO BEGIN VALUES (0); END;
    SET a = 10;
    VALUES (a);
END;
