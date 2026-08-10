-- Snowflake Scripting control flow
-- https://docs.snowflake.com/en/developer-guide/snowflake-scripting/loops
-- https://docs.snowflake.com/en/sql-reference/snowflake-scripting/case

BEGIN
    LET x INTEGER := 0;
    WHILE (x < 10) DO
        x := x + 1;
    END WHILE;
    RETURN x;
END;

BEGIN
    LET x INTEGER := 0;
    WHILE (x < 10) LOOP
        x := x + 1;
    END LOOP;
    RETURN x;
END;

BEGIN
    LET total INTEGER := 0;
    FOR i IN 1 TO 10 DO
        total := total + i;
    END FOR;
    RETURN total;
END;

BEGIN
    LET total INTEGER := 0;
    FOR i IN REVERSE 1 TO 10 DO
        total := total + i;
    END FOR;
    RETURN total;
END;

BEGIN
    LET counter INTEGER := 0;
    LOOP
        counter := counter + 1;
        IF (counter > 5) THEN
            BREAK;
        END IF;
    END LOOP;
    RETURN counter;
END;

BEGIN
    LET counter INTEGER := 0;
    REPEAT
        counter := counter + 1;
    UNTIL (counter > 5)
    END REPEAT;
    RETURN counter;
END;

BEGIN
    LET counter INTEGER := 0;
    LOOP
        counter := counter + 1;
        IF (counter < 5) THEN
            CONTINUE;
        END IF;
        BREAK;
    END LOOP;
    RETURN counter;
END;

BEGIN
    LET result VARCHAR := '';
    CASE (result)
        WHEN 'a' THEN
            result := 'was a';
        WHEN 'b' THEN
            result := 'was b';
        ELSE
            result := 'other';
    END CASE;
    RETURN result;
END;

BEGIN
    LET x INTEGER := 5;
    LET result VARCHAR := '';
    CASE
        WHEN x < 3 THEN
            result := 'small';
        WHEN x < 10 THEN
            result := 'medium';
        ELSE
            result := 'large';
    END;
    RETURN result;
END;

-- Nested loops
BEGIN
    LET total INTEGER := 0;
    FOR i IN 1 TO 3 DO
        LET j INTEGER := 0;
        WHILE (j < 3) DO
            j := j + 1;
            total := total + 1;
        END WHILE;
    END FOR;
    RETURN total;
END;
