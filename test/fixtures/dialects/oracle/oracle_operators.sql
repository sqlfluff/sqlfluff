-- Test Oracle-specific arithmetic operators: ** (power) and MOD

BEGIN
  -- Power operator in IF statements
  IF i ** 2 > 50 THEN
    DBMS_OUTPUT.PUT_LINE('i squared is greater than 50');
  END IF;

  -- MOD operator in IF statements
  IF i MOD 2 = 0 THEN
    DBMS_OUTPUT.PUT_LINE('i is even number');
  ELSE
    DBMS_OUTPUT.PUT_LINE('i is odd number');
  END IF;

  -- Combined operators in complex expressions
  IF (x + y) ** 3 MOD 10 = 0 THEN
    DBMS_OUTPUT.PUT_LINE('complex expression test');
  END IF;

  -- Power operator in SELECT expressions
  SELECT
    id,
    value ** 2 AS value_squared,
    amount ** 0.5 AS square_root
  FROM test_table;

  -- MOD operator in SELECT expressions
  SELECT
    id,
    amount MOD 100 AS last_two_digits,
    CASE WHEN id MOD 2 = 0 THEN 'Even' ELSE 'Odd' END AS parity
  FROM test_table;

  -- Power operator in WHERE clauses
  SELECT * FROM test_table
  WHERE value ** 2 BETWEEN 100 AND 400;

  -- MOD operator in WHERE clauses
  SELECT * FROM test_table
  WHERE id MOD 5 = 0;

  -- Combined operators in ORDER BY
  SELECT id, value FROM test_table
  ORDER BY value ** 2 DESC, id MOD 10;

  -- Power operator in function calls
  DBMS_OUTPUT.PUT_LINE('Result: ' || TO_CHAR(base ** exponent));

  -- MOD operator in function calls
  DBMS_OUTPUT.PUT_LINE('Remainder: ' || TO_CHAR(dividend MOD divisor));

  -- Nested expressions with both operators
  SELECT
    ((a + b) ** 2) MOD 1000 AS complex_calc
  FROM dual;

  -- Power operator with parentheses for precedence
  SELECT
    2 ** (3 + 1) AS power_with_parens,
    (2 ** 3) + 1 AS parens_around_power
  FROM dual;

  -- MOD operator chaining
  SELECT
    x MOD y MOD z AS chained_mod
  FROM dual;

  -- Mixed with other arithmetic operators
  SELECT
    a + b ** 2 - c MOD d * e AS mixed_arithmetic
  FROM dual;
END;
