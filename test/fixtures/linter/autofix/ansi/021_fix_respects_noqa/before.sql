--noqa: disable=L034
SELECT DISTINCT
    TO_CHAR(a, 'YYYY-MM-dd HH:MM:ss') as the_date,
    a AS b
FROM
    table1
