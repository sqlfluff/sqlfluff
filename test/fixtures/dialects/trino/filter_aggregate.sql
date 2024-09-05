SELECT id,
       COUNT(*) FILTER (WHERE o IS NOT NULL) AS count
FROM (VALUES
    (100, 2, 'a'),
    (100, 1, 'b'),
    (200, NULL, 'c'),
    (200, 2, 'a'),
    (300, NULL, 'b'),
    (300, NULL, 'c')
) t(id, o, value)
GROUP BY id;
