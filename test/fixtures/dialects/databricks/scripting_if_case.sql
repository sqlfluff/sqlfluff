-- IF and CASE statements.
-- https://docs.databricks.com/aws/en/sql/language-manual/control-flow/if-stmt
-- https://docs.databricks.com/aws/en/sql/language-manual/control-flow/case-stmt
BEGIN
    DECLARE choice INT DEFAULT 3;
    IF choice < 2 THEN
        VALUES (1);
    ELSEIF choice < 4 THEN
        VALUES (2);
    ELSE
        VALUES (0);
    END IF;
END;

BEGIN
    CASE choice
        WHEN 1 THEN VALUES (1);
        WHEN 2 THEN VALUES (2);
        ELSE VALUES (0);
    END CASE;
END;

BEGIN
    CASE
        WHEN choice < 2 THEN VALUES (1);
        WHEN choice < 4 THEN VALUES (2);
        ELSE VALUES (0);
    END CASE;
END;
