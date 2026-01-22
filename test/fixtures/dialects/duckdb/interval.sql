-- DuckDB interval expressions
-- https://duckdb.org/docs/stable/sql/data_types/interval

-- Static intervals
SELECT INTERVAL 1 YEAR;

SELECT INTERVAL 5 DAY;

SELECT INTERVAL '1 year';

SELECT INTERVAL '5 days 3 hours';

-- Dynamic intervals with parenthesized expressions
SELECT today() + INTERVAL (1000 * random()) DAY;

SELECT today() + INTERVAL (col1 + 5) HOUR;

SELECT INTERVAL (x * 2) MINUTE;

-- Arithmetic operations with intervals
SELECT today() + INTERVAL 1 YEAR AS col1;

SELECT today() + INTERVAL (1000 * random()) DAY AS col2;

SELECT today() + INTERVAL (col1 + col2) HOUR AS col3;

-- Nested expressions
SELECT INTERVAL ((x + y) * z) SECOND;

SELECT INTERVAL (CASE WHEN x > 0 THEN x ELSE 1 END) DAY;

-- Function calls in intervals
SELECT INTERVAL (abs(x)) MONTH;

SELECT INTERVAL (random() * 100) MICROSECONDS;
