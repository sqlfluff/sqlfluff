-- Procedure call statements (no argument list)

-- Unqualified procedure call (no dot, no parentheses)
BEGIN
  my_procedure;
END;
/

-- Package-qualified procedure call
BEGIN
  pkg.my_procedure;
END;
/

-- Fully schema-qualified procedure call
BEGIN
  schema.pkg.my_procedure;
END;
/

-- Collection method calls (no arguments)
BEGIN
  my_collection.EXTEND;
  my_collection.TRIM;
END;
/

-- Mixed: procedure call and function call with arguments in same block
BEGIN
  my_procedure;
  DBMS_OUTPUT.PUT_LINE('test');
END;
/

-- Multiple procedure calls
BEGIN
  first_proc;
  pkg.second_proc;
  schema.pkg.third_proc;
END;
/

-- Procedure call inside IF block
BEGIN
  IF 1 = 1 THEN
    my_procedure;
  END IF;
END;
/

-- Procedure call inside FOR loop
BEGIN
  FOR i IN 1..10 LOOP
    my_procedure;
  END LOOP;
END;
/

-- Procedure call inside WHILE loop
BEGIN
  WHILE TRUE LOOP
    pkg.my_procedure;
    EXIT;
  END LOOP;
END;
/

-- Procedure call with DECLARE block
DECLARE
  v_count NUMBER := 0;
BEGIN
  my_procedure;
  pkg.my_procedure;
END;
/

-- Inline single-statement BEGIN/END blocks
BEGIN my_procedure; END;
/

BEGIN schema.pkg.my_procedure; END;
/

-- Schema-qualified call mixed with a function call that has arguments
BEGIN
  pkg.my_procedure;
  DBMS_OUTPUT.PUT_LINE('test');
END;
/

-- Schema-qualified call mixed with other statements
BEGIN
  schema.pkg.my_procedure;
  DBMS_OUTPUT.PUT_LINE('done');
END;
/

-- Multiple qualified calls in one block
BEGIN
  pkg.my_procedure;
  schema.pkg.my_procedure;
  DBMS_OUTPUT.PUT_LINE('test');
END;
/

-- Procedure call followed by assignment
DECLARE
  v NUMBER;
BEGIN
  my_procedure;
  v := 1;
  pkg.my_procedure;
END;
/

-- Procedure call inside ELSIF branch
BEGIN
  IF 1 = 1 THEN
    my_procedure;
  ELSIF 2 = 2 THEN
    pkg.my_procedure;
  ELSE
    schema.pkg.my_procedure;
  END IF;
END;
/

-- Procedure call inside nested BEGIN/END
BEGIN
  BEGIN
    my_procedure;
    pkg.my_procedure;
  END;
  schema.pkg.my_procedure;
END;
/

-- Regression: EXCEPTION must not be consumed as a procedure-call identifier.
BEGIN
  my_procedure;
EXCEPTION
  WHEN OTHERS THEN
    pkg.my_procedure;
END;
/

-- Same regression with a schema-qualified call before the handler.
BEGIN
  schema.pkg.my_procedure;
EXCEPTION
  WHEN OTHERS THEN
    NULL;
END;
/
