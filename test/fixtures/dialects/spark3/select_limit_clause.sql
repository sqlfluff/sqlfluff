-- Select the first two rows.
SELECT
    name,
    age
FROM person ORDER BY name LIMIT 2;

-- Specifying ALL option on LIMIT returns all the rows.
SELECT
    name,
    age
FROM person ORDER BY name LIMIT ALL;

-- A function expression as an input to LIMIT.
SELECT
    name,
    age
FROM person ORDER BY name LIMIT length('SPARK');
