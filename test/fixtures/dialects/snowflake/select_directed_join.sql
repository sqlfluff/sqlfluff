-- Basic DIRECTED JOIN examples
-- https://docs.snowflake.com/en/sql-reference/constructs/join

-- Inner directed join
SELECT a.id, b.name
FROM table_a a
INNER DIRECTED JOIN table_b b ON a.id = b.id;

-- Left outer directed join
SELECT a.id, b.name
FROM table_a a
LEFT OUTER DIRECTED JOIN table_b b ON a.id = b.id;

-- Left directed join (without OUTER keyword)
SELECT a.id, b.name
FROM table_a a
LEFT DIRECTED JOIN table_b b ON a.id = b.id;

-- Right outer directed join
SELECT a.id, b.name
FROM table_a a
RIGHT OUTER DIRECTED JOIN table_b b ON a.id = b.id;

-- Right directed join
SELECT a.id, b.name
FROM table_a a
RIGHT DIRECTED JOIN table_b b ON a.id = b.id;

-- Full outer directed join
SELECT a.id, b.name
FROM table_a a
FULL OUTER DIRECTED JOIN table_b b ON a.id = b.id;

-- Full directed join
SELECT a.id, b.name
FROM table_a a
FULL DIRECTED JOIN table_b b ON a.id = b.id;

-- Just DIRECTED JOIN (implicit inner)
SELECT a.id, b.name
FROM table_a a
DIRECTED JOIN table_b b ON a.id = b.id;

-- Multiple directed joins in a query
SELECT a.id, b.name, c.value
FROM small_table a
INNER DIRECTED JOIN medium_table b ON a.id = b.id
INNER DIRECTED JOIN large_table c ON b.id = c.id;

-- Mixed directed and non-directed joins
SELECT a.id, b.name, c.value
FROM table_a a
INNER DIRECTED JOIN table_b b ON a.id = b.id
LEFT JOIN table_c c ON b.id = c.id;

-- Directed join with USING clause
SELECT *
FROM table_a
INNER DIRECTED JOIN table_b USING (id);
