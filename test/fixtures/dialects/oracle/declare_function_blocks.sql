DECLARE
  TYPE sum_multiples IS TABLE OF PLS_INTEGER INDEX BY PLS_INTEGER;
  n PLS_INTEGER := 5;

  FUNCTION get_sum(multiple IN PLS_INTEGER, num IN PLS_INTEGER)
  RETURN sum_multiples
  IS
    s sum_multiples;
  BEGIN
    RETURN s;
  END get_sum;

BEGIN
  DBMS_OUTPUT.PUT_LINE('Test');
END;
/
