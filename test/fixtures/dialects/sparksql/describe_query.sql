DESCRIBE QUERY SELECT
    age,
    sum(age) AS sum_age
FROM person GROUP BY age;

DESCRIBE QUERY
WITH all_names_cte AS (SELECT name FROM person)

SELECT name FROM all_names_cte;

DESC QUERY VALUES(100, 'John', 10000.20D) AS employee(id, name, salary);

DESC QUERY TABLE person;

DESCRIBE FROM person SELECT age;
