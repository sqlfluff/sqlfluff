SELECT a::STRUCT(y INTEGER) AS b
FROM
    (SELECT {'x': 42} AS a);

SELECT {"id": foo, "name": bar} AS baz
FROM my_table;

SELECT
    CASE
        WHEN foo IS NULL
            THEN NULL
        ELSE {"id": foo, "name": bar}
        END AS baz
FROM my_table;
