-- CUBE within GROUP BY clause
SELECT
    name,
    age,
    count(*) AS record_count
FROM people
GROUP BY CUBE (name, age);

-- ROLLUP within GROUP BY clause
SELECT
    name,
    age,
    count(*) AS record_count
FROM people
GROUP BY ROLLUP (name, age);
