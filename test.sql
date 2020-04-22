SELECT
    CASE
        WHEN (a < 0) THEN 2
        ELSE -- comment
            0 END
FROM t1