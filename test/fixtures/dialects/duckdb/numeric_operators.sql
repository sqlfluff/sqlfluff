-- Test DuckDB numeric operators

-- Exponentiation operators
SELECT 2 ** 3 AS power_double_star;

SELECT 2 ^ 3 AS power_caret;

-- Factorial operator
SELECT 5! AS factorial;

SELECT (3 + 2)! AS factorial_expr;

-- Abs operator using @
SELECT @(-42) AS abs_at_sign;

SELECT @(-5.5) AS abs_at_float;

-- Combined examples
SELECT
    2 ** 3 AS exponentiation_double_star,
    2 ^ 3 AS exponentiation_caret,
    5! AS factorial,
    @(-42) AS abs_at_sign,
    10 // 3 AS integer_division,
    10 % 3 AS modulo;
