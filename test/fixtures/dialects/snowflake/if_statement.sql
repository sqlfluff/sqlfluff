BEGIN
    IF (1 + 1 = 2) THEN
        SELECT 1;
        SELECT 2;
    ELSEIF (2 + 2 = 4) THEN
        SELECT 3;
        SELECT 4;
    ELSEIF (3 + 3 = 6) THEN
        SELECT 5;
        SELECT 6;
    ELSE
        SELECT 7;
        SELECT 8;
    END IF;
END;