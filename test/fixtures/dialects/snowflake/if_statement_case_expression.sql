-- Regression test: a CASE expression inside a non-first statement of an
-- IF/ELSEIF/ELSE scripting block used to be truncated at its own ELSE,
-- because the block's ELSEIF/ELSE/END IF terminators leaked into the
-- statement match.
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
