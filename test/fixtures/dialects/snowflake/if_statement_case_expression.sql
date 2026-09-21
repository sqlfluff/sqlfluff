-- https://docs.snowflake.com/en/sql-reference/snowflake-scripting/if

-- CASE as non-first statement in IF/ELSEIF/ELSE branches
BEGIN
    IF (1 = 1) THEN
        SELECT 1;
        SELECT CASE WHEN 1 = 1 THEN 'a' ELSE 'b' END;
    ELSEIF (2 = 2) THEN
        SELECT 2;
        SELECT CASE WHEN 2 = 2 THEN 'c' ELSE 'd' END;
    ELSE
        SELECT 3;
        SELECT CASE WHEN 3 = 3 THEN 'e' ELSE 'f' END;
    END IF;
END;

-- CASE as sole statement in IF with chained ELSEIF and ELSE
BEGIN
    IF (1 = 1) THEN
        SELECT CASE WHEN 1 = 1 THEN 'a' ELSE 'b' END;
    ELSEIF (2 = 2) THEN
        SELECT CASE WHEN 2 = 2 THEN 'c' ELSE 'd' END;
    ELSEIF (3 = 3) THEN
        SELECT CASE WHEN 3 = 3 THEN 'e' ELSE 'f' END;
    ELSE
        SELECT CASE WHEN 4 = 4 THEN 'g' ELSE 'h' END;
    END IF;
END;

-- Nested IF with CASE inside an ELSEIF branch
BEGIN
    IF (1 = 1) THEN
        SELECT 1;
    ELSEIF (2 = 2) THEN
        IF (3 = 3) THEN
            SELECT CASE WHEN 3 = 3 THEN 'a' ELSE 'b' END;
        END IF;
    END IF;
END;

-- CASE as sole statement in IF-only (no ELSEIF/ELSE)
BEGIN
    IF (1 = 1) THEN
        SELECT CASE WHEN 1 = 1 THEN 'a' ELSE 'b' END;
    END IF;
END;

-- CASE as first of multiple statements in a branch
BEGIN
    IF (1 = 1) THEN
        SELECT CASE WHEN 1 = 1 THEN 'a' ELSE 'b' END;
        SELECT 2;
    END IF;
END;

-- Nested IF inside ELSE branch with CASE
BEGIN
    IF (1 = 1) THEN
        SELECT 1;
    ELSE
        IF (2 = 2) THEN
            SELECT CASE WHEN 1 = 1 THEN 'a' ELSE 'b' END;
        END IF;
    END IF;
END;

-- Deeply nested: IF > ELSEIF > IF > ELSEIF > CASE
BEGIN
    IF (1 = 1) THEN
        SELECT 1;
    ELSEIF (2 = 2) THEN
        IF (3 = 3) THEN
            SELECT 2;
        ELSEIF (4 = 4) THEN
            SELECT CASE WHEN 5 = 5 THEN 'a' ELSE 'b' END;
        END IF;
    END IF;
END;

-- Multiple CASE expressions in every branch
BEGIN
    IF (1 = 1) THEN
        SELECT CASE WHEN 1 = 1 THEN 'a' ELSE 'b' END;
        SELECT CASE WHEN 2 = 2 THEN 'c' ELSE 'd' END;
    ELSEIF (3 = 3) THEN
        SELECT 1;
        SELECT CASE WHEN 3 = 3 THEN 'e' ELSE 'f' END;
        SELECT 2;
    ELSE
        SELECT CASE WHEN 4 = 4 THEN 'g' ELSE 'h' END;
        SELECT 3;
    END IF;
END;
