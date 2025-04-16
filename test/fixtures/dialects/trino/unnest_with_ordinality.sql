-- Single UNNEST argument, 2-argument ordinality.
WITH t AS (
    SELECT ARRAY['a', 'b', 'c'] AS array_column
)

SELECT
    u.element,
    u.ordinality
FROM t
CROSS JOIN UNNEST(t.array_column) WITH ORDINALITY AS u(element, ordinality);

-- Single UNNEST argument, 2-argument ordinality, no 'AS' after ORDINALITY
WITH t AS (
    SELECT ARRAY['a', 'b', 'c'] AS array_column
)

SELECT
    u.element,
    u.ordinality
FROM t
CROSS JOIN UNNEST(t.array_column) WITH ORDINALITY u(element, ordinality);

-- Single UNNEST argument, 2-argument ordinality, space between "u" and ordinality spec.
WITH t AS (
    SELECT ARRAY['a', 'b', 'c'] AS array_column
)

SELECT
    u.element,
    u.ordinality
FROM t
CROSS JOIN UNNEST(t.array_column) WITH ORDINALITY u (element, ordinality);

-- Multiple UNNEST arguments, 3-argument ordinality.
WITH t AS (
    SELECT
        ARRAY['a', 'b', 'c'] AS array_column1,
        ARRAY[1, 2] AS array_column2
)

SELECT
    u.element1,
    u.element2,
    u.ordinality
FROM t
CROSS JOIN UNNEST(t.array_column1, t.array_column2) WITH ORDINALITY AS u(element1, element2, ordinality);

-- A basic UNNEST, no ORDINALITY
WITH t AS (
    SELECT ARRAY[1, 2] AS array_column
)

SELECT u.number
FROM t
CROSS JOIN UNNEST(t.array_column) AS u (number);
