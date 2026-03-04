SELECT
	ROW_NUMBER() OVER (PARTITION BY col_1) AS row
FROM table
QUALIFY row = 1;

SELECT
    *
FROM table
QUALIFY ROW_NUMBER() OVER (PARTITION BY col_1) = 1;

SELECT
    ROW_NUMBER() OVER (PARTITION BY col_1) AS row
FROM table
WHERE col_1 = 'active'
QUALIFY row = 1;

SELECT
     *
FROM table
WHERE col_1 = 'active'
QUALIFY ROW_NUMBER() OVER (PARTITION BY col_1) = 1;

SELECT
     *
FROM table
WHERE col_1 = 'active'
WINDOW test_window AS (PARTITION BY col_1)
QUALIFY ROW_NUMBER() OVER test_window = 1;

SELECT
    ROW_NUMBER() OVER (PARTITION BY col_1) AS row
FROM table1
JOIN table2
ON table1.col_1 = table2.col_1
QUALIFY row = 1;

SELECT
     *
FROM table1
JOIN table2
ON table1.col_1 = table2.col_1
QUALIFY ROW_NUMBER() OVER (PARTITION BY col_1) = 1;

SELECT
    ROW_NUMBER() OVER (PARTITION BY col_1) AS row
FROM table1
JOIN table2
ON table1.col_1 = table2.col_1
WHERE table1.col_1 = 'active'
QUALIFY row = 1;

SELECT
     *
FROM table1
JOIN table2
ON table1.col_1 = table2.col_1
WHERE table1.col_1 = 'active'
QUALIFY ROW_NUMBER() OVER (PARTITION BY col_1) = 1;

SELECT
     *
FROM table1
JOIN table2
ON table1.col_1 = table2.col_1
WHERE table1.col_1 = 'active'
WINDOW test_window AS (PARTITION BY table1.col_1)
QUALIFY ROW_NUMBER() OVER test_window = 1;

SELECT
    table2.col_a,
    table1.col_b,
    count(*) AS total,
    row_number() OVER (PARTITION BY table1.col_b ORDER BY count(*) DESC) AS rank
FROM table1
LEFT JOIN table2 ON table1.col_1 = table2.col_1
WHERE table1.col_1 LIKE '%test%'
GROUP BY table2.col_a,table1.col_b
QUALIFY rank = 1;

SELECT
    table2.col_a,
    table1.col_b,
    count(*) AS total,
    row_number() OVER (PARTITION BY table1.col_b ORDER BY count(*) DESC) AS rank
FROM table1
LEFT JOIN table2 ON table1.col_1 = table2.col_1
WHERE table1.col_1 LIKE '%test%'
GROUP BY table2.col_a,table1.col_b
HAVING count(*) > 1
QUALIFY rank = 1;

SELECT
    table2.col_a,
    table1.col_b,
    count(*) AS total,
    row_number() OVER (PARTITION BY table1.col_b ORDER BY count(*) DESC) AS rank
FROM table1
LEFT JOIN table2 ON table1.col_1 = table2.col_1
WHERE table1.col_1 LIKE '%test%'
GROUP BY table2.col_a,table1.col_b
HAVING count(*) > 1
QUALIFY rank = 1
ORDER BY total;

SELECT
    table2.col_a,
    table1.col_b,
    count(*) AS total,
    row_number() OVER (PARTITION BY table1.col_b ORDER BY count(*) DESC) AS rank
FROM table1
LEFT JOIN table2 ON table1.col_1 = table2.col_1
WHERE table1.col_1 LIKE '%test%'
GROUP BY table2.col_a,table1.col_b
HAVING count(*) > 1
QUALIFY rank = 1
LIMIT 1;

SELECT
    table2.col_a,
    table1.col_b,
    count(*) AS total,
    row_number() OVER (PARTITION BY table1.col_b ORDER BY count(*) DESC) AS rank
FROM table1
LEFT JOIN table2 ON table1.col_1 = table2.col_1
WHERE table1.col_1 LIKE '%test%'
GROUP BY table2.col_a,table1.col_b
HAVING count(*) > 1
QUALIFY rank = 1
ORDER BY total
LIMIT 1;

SELECT
    table2.col_a,
    table1.col_b,
    count(*) AS total,
    row_number() OVER (PARTITION BY table1.col_b ORDER BY count(*) DESC) AS rank
FROM table1
LEFT JOIN table2 ON table1.col_1 = table2.col_1
WHERE table1.col_1 LIKE '%test%'
GROUP BY table2.col_a,table1.col_b
HAVING count(*) > 1
QUALIFY rank = 1
ORDER BY total
LIMIT 1 BY table2.col_a;
