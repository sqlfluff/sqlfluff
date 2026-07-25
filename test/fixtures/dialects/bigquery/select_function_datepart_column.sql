-- Columns named after date parts should parse as column references in
-- functions which don't take date part arguments.
-- https://github.com/sqlfluff/sqlfluff/issues/5015
SELECT REGEXP_EXTRACT(year, r"[0-9]{4}")
FROM some_table;

-- Date part functions should still parse date parts.
SELECT
    EXTRACT(YEAR FROM some_date),
    DATE_TRUNC(some_date, WEEK(MONDAY)),
    DATE_DIFF(date_a, date_b, DAY)
FROM some_table;
