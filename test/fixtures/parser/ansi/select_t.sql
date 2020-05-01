SELECT
    *
FROM
    TABLE_1
    FULL OUTER JOIN  -- comment1
    (
        SELECT
            *
        FROM Table_B
        WHERE COL_2 = 'B'
        UNION ALL
        SELECT
            *
        FROM TABLE_C
        WHERE
            COL_1 = 0
    )
ON TABLE_1.A = TABLE_2.A
