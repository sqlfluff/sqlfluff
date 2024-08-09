--https://trino.io/docs/current/functions/aggregate.html#array_agg

SELECT listagg(value, ',') WITHIN GROUP (ORDER BY value) csv_value
FROM (VALUES 'a', 'c', 'b') t(value);

SELECT listagg(value, ',' ON OVERFLOW ERROR) WITHIN GROUP (ORDER BY value) csv_value
FROM (VALUES 'a', 'b', 'c') t(value);

SELECT LISTAGG(value, ',' ON OVERFLOW TRUNCATE '.....' WITH COUNT) WITHIN GROUP (ORDER BY value)
FROM (VALUES 'a', 'b', 'c') t(value);

SELECT id, LISTAGG(value, ',') WITHIN GROUP (ORDER BY o) csv_value
FROM (VALUES
    (100, 1, 'a'),
    (200, 3, 'c'),
    (200, 2, 'b')
) t(id, o, value)
GROUP BY id
ORDER BY id;

-- Handle a WITHIN GROUP followed by a FILTER
SELECT id, LISTAGG(value, ',') WITHIN GROUP (ORDER BY o) FILTER (WHERE o IS NOT NULL) AS csv_value
FROM (VALUES
    (100, 2, 'a'),
    (100, 1, 'b'),
    (200, NULL, 'c'),
    (200, 2, 'a'),
    (300, NULL, 'b'),
    (300, 1, 'c')
) t(id, o, value)
GROUP BY id
ORDER BY id;
