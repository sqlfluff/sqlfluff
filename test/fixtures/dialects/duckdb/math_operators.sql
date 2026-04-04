-- Test DuckDB math operators: @, !, **

-- Absolute value prefix operator (@)
SELECT @(-42) AS abs_value;

SELECT @(col1) FROM table1;

SELECT @(-3.14) AS abs_pi;

-- Factorial postfix operator (!)
SELECT 5! AS factorial_5;

SELECT 0! AS factorial_0;

SELECT col1! FROM table1;

-- Exponentiation operator (**)
SELECT 2 ** 3 AS power_result;

SELECT 10 ** -2 AS negative_exp;

SELECT col1 ** 2 FROM table1;

-- Combined operators
SELECT @(-5)!, (2 ** 3)!, @(4 ** 2);

-- In expressions
SELECT
    @(-42) AS abs_alias,
    5! AS factorial_op,
    2 ** 3 AS exponentiation_1,
    @(col1) AS abs_col,
    col2! AS fact_col,
    col3 ** 2 AS squared
FROM my_table
WHERE @(value) > 10
    AND result! < 1000
    AND base ** exp = 64;
