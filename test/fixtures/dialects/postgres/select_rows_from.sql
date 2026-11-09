SELECT * FROM ROWS FROM (generate_series(1, 3));

SELECT * FROM ROWS FROM (generate_series(1, 3), unnest(ARRAY[1, 2])) AS x (a, b);

SELECT *
FROM ROWS FROM (generate_series(1, 3), unnest(ARRAY[1, 2])) WITH ORDINALITY AS x (a, b, n);

SELECT *
FROM ROWS FROM (
    json_to_record('{"a": 1, "b": "x"}') AS (a int, b text),
    generate_series(1, 2)
) AS t (a, b, n);

SELECT *
FROM tbl, LATERAL ROWS FROM (generate_series(1, tbl.n)) AS g (i);
