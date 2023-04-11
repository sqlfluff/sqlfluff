-- Sort rows
SELECT
    name,
    age
FROM person ORDER BY age;

-- Sort rows in ascending manner keeping null values to be last.
SELECT
    name,
    age
FROM person ORDER BY age NULLS LAST;

-- Sort rows in descending manner, which defaults to NULL LAST.
SELECT
    name,
    age
FROM person ORDER BY age DESC;

-- Sort rows in ascending manner keeping null values to be first.
SELECT
    name,
    age
FROM person ORDER BY age DESC NULLS FIRST;

-- Sort rows based on more than one column with each column having different
-- sort direction.
SELECT
    name,
    age
FROM person ORDER BY name ASC, age DESC;

-- Sort rows using complex expression.
SELECT
    name,
    age
FROM person ORDER BY SUM(age)/SUM(age) DESC;
