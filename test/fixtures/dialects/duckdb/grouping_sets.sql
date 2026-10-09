SELECT city, street_name, avg(income)
FROM addresses
GROUP BY GROUPING SETS ((city, street_name), (city), (street_name), ());

SELECT city, street_name, avg(income)
FROM addresses
GROUP BY CUBE (city, street_name);

SELECT city, street_name, avg(income)
FROM addresses
GROUP BY ROLLUP (city, street_name);

SELECT
    course,
    type,
    count(*),
    grouping(course) AS grouping_course,
    grouping_id(course, type) AS grouping_all
FROM students
GROUP BY GROUPING SETS ((course, type), course, type, ())
ORDER BY ALL;

SELECT country, city, street_name, sum(income)
FROM addresses
GROUP BY country, ROLLUP (city, street_name);

SELECT count(*)
FROM addresses
GROUP BY ();
