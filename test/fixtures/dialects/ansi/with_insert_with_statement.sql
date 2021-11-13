WITH mycte1 AS (
    SELECT
        foo,
        bar,
        baz
    FROM mytable
)

INSERT INTO table2 (column1, column2, column3)
WITH mycte2 AS (
    SELECT
        foo,
        bar,
        baz
    FROM mycte1
)

SELECT
    foo,
    bar,
    baz
FROM mycte2;
