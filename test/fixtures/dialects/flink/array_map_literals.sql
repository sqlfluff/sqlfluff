SELECT
    ARRAY[1, 2, 3] AS numbers,
    ARRAY['a', 'b'] AS strings,
    ARRAY[ARRAY[1, 2], ARRAY[3]] AS nested,
    MAP['a', 1, 'b', 2] AS lookup,
    ARRAY[1, 2, 3][1] AS first_number
FROM my_table;

SELECT *
FROM my_table
CROSS JOIN UNNEST(ARRAY['a', 'b']) AS t (letter);
