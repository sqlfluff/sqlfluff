-- Test that GROUP BY properly terminates before the next statement
-- Without a semicolon terminator, the parser should still recognize
-- that a new SELECT statement starts a new query, not continues GROUP BY

-- QUERY 1: Simple GROUP BY followed by another query
SELECT FIELD2
FROM TABLE2
GROUP BY
    FIELD3

-- QUERY 2: UNION query with 2 columns
SELECT
    FIELD1,
    FIELD2
FROM TABLE2

UNION ALL

SELECT
    FIELD3,
    FIELD4
FROM TABLE3

-- edge cases
-- Test various GROUP BY termination scenarios

-- Test 1: GROUP BY followed by SELECT (without semicolon)
SELECT FIELD1
FROM TABLE1
GROUP BY FIELD1

SELECT FIELD2
FROM TABLE2

-- Test 2: GROUP BY followed by UNION (should be separate queries)
SELECT FIELD1
FROM TABLE1
GROUP BY FIELD1

SELECT FIELD2
FROM TABLE2
UNION ALL
SELECT FIELD3
FROM TABLE3

-- Test 3: GROUP BY followed by HAVING (same query)
SELECT FIELD1, COUNT(*)
FROM TABLE1
GROUP BY FIELD1
HAVING COUNT(*) > 1

-- Test 4: GROUP BY followed by ORDER BY (same query)
SELECT FIELD1, COUNT(*)
FROM TABLE1
GROUP BY FIELD1
ORDER BY COUNT(*) DESC

-- Test 5: GROUP BY with WITH ROLLUP followed by SELECT
SELECT FIELD1, COUNT(*)
FROM TABLE1
GROUP BY FIELD1 WITH ROLLUP

SELECT FIELD2
FROM TABLE2

-- Test 6: GROUP BY followed by OPTION clause (same query)
SELECT FIELD1, COUNT(*)
FROM TABLE1
GROUP BY FIELD1
OPTION (MAXDOP 4)

-- Test 7: Multiple GROUP BY expressions
SELECT FIELD1, FIELD2, COUNT(*)
FROM TABLE1
GROUP BY
    FIELD1,
    FIELD2,
    YEAR(DateField)

SELECT FIELD3
FROM TABLE2
