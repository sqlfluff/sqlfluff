UPDATE table_name
FROM
(
    SELECT
       a, b, c, d
    FROM
        t_b INNER JOIN t_c
        ON t_b.d = t_c.d

    WHERE
       b = 'F'
       -- AND SUBSTR(c, 1, 1) = 'T'

) AS t_d
SET
    column1 = value1,
    column2 = 'value2'
WHERE a=1;
