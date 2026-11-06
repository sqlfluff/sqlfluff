SELECT *
FROM (
    SELECT a
    FROM t
) x
JOIN y ON x.a = y.a;
