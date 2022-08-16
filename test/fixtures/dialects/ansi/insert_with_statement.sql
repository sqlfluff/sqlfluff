INSERT INTO table2 (column1, column2, column3)
WITH mycte AS (
    SELECT
        foo,
        bar
    FROM mytable1
)

SELECT
    foo,
    bar,
    baz
FROM mycte;
