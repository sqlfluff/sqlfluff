-- OVERLAPS binds two operands, so it also works where a boolean is expected.
-- https://github.com/sqlfluff/sqlfluff/issues/2492
SELECT
    CASE
        WHEN (current_date, current_date + 7) OVERLAPS (DATE '2021-01-01', DATE '2021-01-07') THEN 1
        ELSE 0
    END AS strt_yr
FROM tbl;

SELECT col1
FROM tbl
WHERE (start_date, end_date) OVERLAPS (DATE '2021-01-01', DATE '2021-01-07');

SELECT col1
FROM tbl
WHERE period1 OVERLAPS period2;
