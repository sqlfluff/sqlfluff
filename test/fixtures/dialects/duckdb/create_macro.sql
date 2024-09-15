CREATE MACRO add(a, b) AS a + b;
CREATE MACRO ifelse(a, b, c) AS CASE WHEN a THEN b ELSE c END;
CREATE MACRO one() AS (SELECT 1);
CREATE MACRO plus_one(a) AS (
    WITH cte AS (SELECT 1 AS a)

    SELECT cte.a + cte.a FROM cte
);
CREATE FUNCTION main.my_avg(x) AS sum(x) / count(x);
CREATE MACRO add_default(a, b := 5) AS a + b;
CREATE MACRO arr_append(l, e) AS list_concat(l, list_value(e));

CREATE MACRO static_table() AS TABLE
    SELECT
        'Hello' AS column1,
        'World' AS column2;

CREATE MACRO dynamic_table(col1_value, col2_value) AS TABLE
    SELECT
        col1_value AS column1,
        col2_value AS column2;

CREATE OR REPLACE TEMP MACRO dynamic_table(col1_value, col2_value) AS TABLE
    SELECT
        col1_value AS column1,
        col2_value AS column2
    UNION ALL
    SELECT
        'Hello' AS col1_value,
        456 AS col2_value;

CREATE MACRO get_users(i) AS TABLE
    SELECT * FROM users WHERE uid IN (SELECT unnest(i));

CREATE OR REPLACE MACRO list_builder(
    col1,
    col2
) AS
CASE
    WHEN col1 AND col2 THEN ['x', 'y']
    WHEN col1 THEN ['x']
    WHEN col2 THEN ['y']
    ELSE
        []
END;
