(
    SELECT * FROM tbl1
    EXCEPT
    SELECT * FROM tbl2
)
UNION ALL
(
    SELECT * FROM tbl2
    EXCEPT
    SELECT * FROM tbl1
    ORDER BY column_1
)
ORDER BY column_2;
