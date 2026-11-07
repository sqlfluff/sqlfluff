CREATE PROCEDURE p1(i INT)
BEGIN
    DECLARE a INT;
    -- A block as a branch's only statement, and an empty block as the
    -- "no match is fine" ELSE, which avoids error 1339 (case not found).
    CASE i
        WHEN 1 THEN
            BEGIN
                SET a = 1;
                SET a = a + 1;
            END;
        ELSE
            BEGIN
            END;
    END CASE;
    -- A labelled block, left from inside a branch.
    CASE
        WHEN i > 0 THEN
            lbl: BEGIN
                IF i > 10 THEN
                    LEAVE lbl;
                END IF;
                SET a = i;
            END lbl;
        ELSE BEGIN END;
    END CASE;
END
