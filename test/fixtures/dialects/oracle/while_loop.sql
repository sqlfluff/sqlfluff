DECLARE
  done  BOOLEAN := FALSE;
BEGIN
  WHILE done LOOP
    DBMS_OUTPUT.PUT_LINE ('This line does not print.');
    done := TRUE;  -- This assignment is not made.
  END LOOP;

  WHILE NOT done LOOP
    DBMS_OUTPUT.PUT_LINE ('Hello, world!');
    done := TRUE;
  END LOOP;
END;
/

-- Nested WHILE loops with an end-label on the inner loop.
-- Regression: without exclude=Ref.keyword("END") on the optional leading
-- label in LoopStatementSegment, the parser could treat END (of the outer
-- block) as a loop label, consuming it before the enclosing structure could
-- claim it and breaking the entire parse.
BEGIN
  WHILE TRUE LOOP
    WHILE TRUE LOOP
      NULL;
    END LOOP inner_loop;
    EXIT;
  END LOOP;
END;
/

-- Same regression with a FOR loop outer body.
BEGIN
  FOR i IN 1..3 LOOP
    FOR j IN 1..3 LOOP
      NULL;
    END LOOP inner_loop;
  END LOOP outer_loop;
END;
/
