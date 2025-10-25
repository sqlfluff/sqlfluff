-- Test 1: Simple CASE expression (CASE WHEN)
SELECT
    CASE
        WHEN x = 5 THEN 1
        WHEN x = 10 THEN 2
        ELSE 0
    END AS result
FROM abc;

-- Test 2: Simple CASE expression without ELSE
SELECT
    CASE
        WHEN x = 5 THEN 1
        WHEN x = 10 THEN 2
    END AS result
FROM abc;

-- Test 3: Searched CASE expression with nested CASE
SELECT
    CASE
        WHEN x = 5 THEN
            CASE
                WHEN y = 6 THEN 999
            END
    END AS hi
FROM abc;

-- Test 4: Searched CASE with nested CASE and ELSE
SELECT
    CASE
        WHEN x = 5 THEN
            CASE
                WHEN y = 6 THEN 999
                ELSE 888
            END
        ELSE 777
    END AS result
FROM abc;

-- Test 5: Simple CASE expression (CASE expr WHEN)
SELECT
    CASE x
        WHEN 5 THEN 1
        WHEN 10 THEN 2
        ELSE 0
    END AS result
FROM abc;

-- Test 6: Simple CASE expression with nested CASE
SELECT
    CASE x
        WHEN 5 THEN
            CASE y
                WHEN 6 THEN 999
                ELSE 888
            END
        WHEN 10 THEN 2
        ELSE 0
    END AS result
FROM abc;

-- Test 7: Complex nested CASE expressions
SELECT
    CASE
        WHEN x = 5 THEN
            CASE
                WHEN y = 6 THEN
                    CASE z
                        WHEN 7 THEN 777
                        WHEN 8 THEN 888
                        ELSE 999
                    END
                ELSE 666
            END
        WHEN x = 10 THEN
            CASE y
                WHEN 11 THEN 111
                ELSE 222
            END
        ELSE 333
    END AS complex_result
FROM abc;

-- Test 8: CASE expressions in WHERE clause
SELECT *
FROM abc
WHERE CASE
    WHEN x = 5 THEN 1
    WHEN x = 10 THEN 2
    ELSE 0
END = 1;

-- Test 9: CASE expressions in ORDER BY
SELECT x, y, z
FROM abc
ORDER BY CASE
    WHEN x = 5 THEN 1
    WHEN x = 10 THEN 2
    ELSE 3
END;

-- Test 10: CASE expressions with functions
SELECT
    CASE
        WHEN LENGTH(name) > 10 THEN 'Long'
        WHEN LENGTH(name) > 5 THEN 'Medium'
        ELSE 'Short'
    END AS name_length
FROM abc;

-- Test 11: CASE expressions with NULL handling
SELECT
    CASE
        WHEN x IS NULL THEN 'NULL'
        WHEN x = 0 THEN 'Zero'
        WHEN x > 0 THEN 'Positive'
        ELSE 'Negative'
    END AS x_status
FROM abc;

-- Test 12: CASE expressions with multiple conditions
SELECT
    CASE
        WHEN x = 5 AND y = 6 THEN 'Both match'
        WHEN x = 5 OR y = 6 THEN 'One matches'
        ELSE 'Neither matches'
    END AS condition_result
FROM abc;

-- Test 13: CASE expressions with subqueries
SELECT
    CASE
        WHEN x = 5 THEN (SELECT MAX(id) FROM def WHERE id = x)
        WHEN x = 10 THEN (SELECT MIN(id) FROM def WHERE id = x)
        ELSE 0
    END AS subquery_result
FROM abc;

-- Test 14: CASE expressions with type conversion
SELECT
    CASE
        WHEN x = 5 THEN TO_CHAR(x, '999')
        WHEN x = 10 THEN TO_NUMBER('10')
        ELSE 'Unknown'
    END AS converted_result
FROM abc;

-- Test 15: CASE expressions in UPDATE statement
UPDATE abc
SET status = CASE
    WHEN x = 5 THEN 'Active'
    WHEN x = 10 THEN 'Inactive'
    ELSE 'Unknown'
END
WHERE id = 1;

-- Test 16: CASE expressions in INSERT statement
INSERT INTO abc (id, status)
SELECT id, CASE
    WHEN x = 5 THEN 'Active'
    WHEN x = 10 THEN 'Inactive'
    ELSE 'Unknown'
END
FROM def;

-- Test 17: CASE expressions with date handling
SELECT
    CASE
        WHEN created_date > SYSDATE - 1 THEN 'Recent'
        WHEN created_date > SYSDATE - 7 THEN 'This week'
        WHEN created_date > SYSDATE - 30 THEN 'This month'
        ELSE 'Old'
    END AS age_category
FROM abc;

-- Test 18: CASE expressions with string operations
SELECT
    CASE
        WHEN UPPER(name) LIKE '%TEST%' THEN 'Test record'
        WHEN LOWER(name) LIKE '%prod%' THEN 'Production record'
        ELSE 'Other'
    END AS record_type
FROM abc;

-- Test 19: CASE expressions with numeric operations
SELECT
    CASE
        WHEN x + y > 100 THEN 'High sum'
        WHEN x * y > 50 THEN 'High product'
        WHEN x - y < 0 THEN 'Negative difference'
        ELSE 'Normal'
    END AS calculation_result
FROM abc;

-- Test 20: CASE expressions with EXISTS subqueries
SELECT
    CASE
        WHEN EXISTS (SELECT 1 FROM def WHERE def.id = abc.x) THEN 'Exists in def'
        WHEN EXISTS (SELECT 1 FROM ghi WHERE ghi.id = abc.y) THEN 'Exists in ghi'
        ELSE 'Not found'
    END AS existence_check
FROM abc;

-- Test 21: CASE expressions with IN operator
SELECT
    CASE
        WHEN x IN (1, 2, 3) THEN 'Low'
        WHEN x IN (4, 5, 6) THEN 'Medium'
        WHEN x IN (7, 8, 9) THEN 'High'
        ELSE 'Unknown'
    END AS range_category
FROM abc;

-- Test 22: CASE expressions with BETWEEN
SELECT
    CASE
        WHEN x BETWEEN 1 AND 10 THEN 'First range'
        WHEN x BETWEEN 11 AND 20 THEN 'Second range'
        WHEN x BETWEEN 21 AND 30 THEN 'Third range'
        ELSE 'Out of range'
    END AS between_result
FROM abc;

-- Test 23: CASE expressions with REGEXP_LIKE
SELECT
    CASE
        WHEN REGEXP_LIKE(name, '^[A-Z]') THEN 'Starts with uppercase'
        WHEN REGEXP_LIKE(name, '[0-9]') THEN 'Contains number'
        ELSE 'Other pattern'
    END AS pattern_match
FROM abc;

-- Test 24: CASE expressions with DECODE equivalent
SELECT
    CASE x
        WHEN 1 THEN 'One'
        WHEN 2 THEN 'Two'
        WHEN 3 THEN 'Three'
        ELSE 'Other'
    END AS decode_equivalent
FROM abc;

-- Test 25: Complex nested CASE with multiple levels
SELECT
    CASE
        WHEN x = 1 THEN
            CASE y
                WHEN 10 THEN
                    CASE z
                        WHEN 100 THEN 'Level 3 - 100'
                        WHEN 200 THEN 'Level 3 - 200'
                        ELSE 'Level 3 - Other'
                    END
                WHEN 20 THEN 'Level 2 - 20'
                ELSE 'Level 2 - Other'
            END
        WHEN x = 2 THEN
            CASE y
                WHEN 30 THEN 'Level 2 - 30'
                ELSE 'Level 2 - Other'
            END
        ELSE 'Level 1 - Other'
    END AS multi_level_result
FROM abc;

-- Test 26: CASE expression ending with END CASE
SELECT
    CASE
        WHEN x = 5 THEN 1
        WHEN x = 10 THEN 2
        ELSE 0
    END CASE AS result
FROM abc;

-- Test 27: CASE expression ending with END identifier
SELECT
    CASE
        WHEN x = 5 THEN 1
        WHEN x = 10 THEN 2
        ELSE 0
    END my_case AS result
FROM abc;

-- Test 28: CASE expression with bracketed condition
SELECT
    CASE
        WHEN abc = 1 THEN NULL
        WHEN (
            defg = 2
            AND hijk = 3
        ) THEN NULL
    END AS result
FROM abc;
