-- with insert statement with `AS` keyword
WITH mycte AS (
    SELECT
        foo,
        bar,
        baz
    FROM mytable1
)

INSERT INTO table2 (column1, column2, column3)
VALUES ('value1', 'value2', 'value3');

-- with statement without `AS` keyword
WITH mycte (
    SELECT
        foo,
        bar,
        baz
    FROM mytable1
)

INSERT INTO table2 (column1, column2, column3)
VALUES ('value1', 'value2', 'value3');
