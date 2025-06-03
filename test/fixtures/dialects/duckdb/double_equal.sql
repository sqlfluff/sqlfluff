SELECT
    COALESCE(
        MAX(CASE WHEN col1 == 'A' THEN cola END),
        MAX(CASE WHEN col1 == 'B' THEN colb END),
        MAX(CASE WHEN col1 = 'C' THEN colb END)
    ) AS result
FROM my_table;
