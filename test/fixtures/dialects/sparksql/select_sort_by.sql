-- Sort rows within each partition in ascending manner
SELECT /*+ REPARTITION(zip_code) */
    name,
    age,
    zip_code
FROM person
SORT BY
    name;

SELECT
    name,
    age,
    zip_code
FROM person
SORT BY
    name;

-- Sort rows within each partition using column position.
SELECT /*+ REPARTITION(zip_code) */
    name,
    age,
    zip_code
FROM person
SORT BY 1;

SELECT
    name,
    age,
    zip_code
FROM person
SORT BY 1;

-- Sort rows within partition in ascending
-- manner keeping null values to be last.
SELECT /*+ REPARTITION(zip_code) */
    age,
    name,
    zip_code
FROM person
SORT BY
    age NULLS LAST;

SELECT
    age,
    name,
    zip_code
FROM person
SORT BY
    age NULLS LAST;

-- Sort rows by age within each partition in
-- descending manner, which defaults to NULL LAST.
SELECT /*+ REPARTITION(zip_code) */
    age,
    name,
    zip_code
FROM person
SORT BY
    age DESC;

SELECT
    age,
    name,
    zip_code
FROM person
SORT BY
    age DESC;

-- Sort rows by age within each partition in
-- descending manner keeping null values to be first.
SELECT /*+ REPARTITION(zip_code) */
    age,
    name,
    zip_code
FROM person
SORT BY
    age DESC NULLS FIRST;

SELECT
    age,
    name,
    zip_code
FROM person
SORT BY
    age DESC NULLS FIRST;

-- Sort rows within each partition based on more
-- than one column with each column having different
-- sort direction.
SELECT /*+ REPARTITION(zip_code) */
    name,
    age,
    zip_code
FROM person
SORT BY
    name ASC, age DESC;

SELECT
    name,
    age,
    zip_code
FROM person
SORT BY
    name ASC, age DESC;

-- Sort rows within each partition based on result of a function.
SELECT
    age,
    name
FROM person
SORT BY
    LEFT(SUBSTRING_INDEX(name, ' ', -1), 1);

SELECT
    age,
    name
FROM person
WHERE age <= 100
SORT BY age;

SELECT
    age,
    name
FROM person
GROUP BY age
SORT BY age;

SELECT
    age,
    name
FROM person
GROUP BY age
HAVING COUNT(age) > 1
SORT BY age;

SELECT CURRENT_DATE() AS p_data_date
SORT BY p_data_date;
