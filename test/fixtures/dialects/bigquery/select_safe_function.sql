SELECT
    TRUE AS col1,
    SAFE.SUBSTR('foo', 0, -2) AS col2,
    SAFE.DATEADD(DAY, -2, CURRENT_DATE),
    SAFE.MY_FUNCTION(column1)
FROM
    table1;
