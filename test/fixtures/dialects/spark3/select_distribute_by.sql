-- Produces rows clustered by age. Persons with same age are clustered together.
-- Unlike `CLUSTER BY` clause, the rows are not sorted within a partition.
SELECT
    age,
    name
FROM person
DISTRIBUTE BY
    age;

SELECT
    age,
    name
FROM person
DISTRIBUTE BY
    1;

SELECT
    age,
    name
FROM person
DISTRIBUTE BY
    name,
    age;

SELECT
    age,
    name
FROM person
DISTRIBUTE BY
    LEFT(SUBSTRING_INDEX(name, ' ', -1), 1);
