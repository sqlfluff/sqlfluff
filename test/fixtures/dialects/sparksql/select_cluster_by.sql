-- Produces rows clustered by age. Persons with same age are clustered together.
-- In the query below, persons with age 18 and 25 are in first partition and the
-- persons with age 16 are in the second partition. The rows are sorted based
-- on age within each partition.
SELECT
    age,
    name
FROM person
CLUSTER BY
    age;

SELECT
    age,
    name
FROM person
CLUSTER BY
    1;

SELECT
    age,
    name
FROM person
CLUSTER BY
    name,
    age;

SELECT
    age,
    name
FROM person
CLUSTER BY
    LEFT(SUBSTRING_INDEX(name, ' ', -1), 1);

SELECT
    age,
    name
FROM person
WHERE age <= 100
CLUSTER BY age;

SELECT
    age,
    name
FROM person
GROUP BY age
CLUSTER BY age;

SELECT
    age,
    name
FROM person
GROUP BY age
HAVING COUNT(age) > 1
CLUSTER BY age;

SELECT
    age,
    name
FROM person
UNION ALL
SELECT
    age,
    name
FROM person_cold
CLUSTER BY age;

SELECT CURRENT_DATE() AS p_data_date
CLUSTER BY p_data_date;
