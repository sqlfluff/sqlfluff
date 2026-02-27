-- Example 1: Procedure with slash buffer executor
CREATE OR REPLACE PROCEDURE proc1 AS
BEGIN
  DBMS_OUTPUT.PUT_LINE('Procedure 1');
END;
/

-- Example 2: Function with slash buffer executor
CREATE OR REPLACE FUNCTION func1 RETURN VARCHAR2 AS
BEGIN
  RETURN 'Function 1';
END;
/

-- Example 3: Anonymous block with slash buffer executor
BEGIN
  DBMS_OUTPUT.PUT_LINE('Anonymous block');
END;
/

-- Example 4: Another procedure
CREATE OR REPLACE PROCEDURE proc2 AS
BEGIN
  DBMS_OUTPUT.PUT_LINE('Procedure 2');
END;
/

-- Example 5: Function with multiline comment before the slash buffer executor
CREATE OR REPLACE FUNCTION func3 RETURN VARCHAR2 AS
BEGIN
  RETURN 'Function with comments';
END;
/*
  This is a multiline comment
  right after the function body
*/
/
-- A comment after the slash buffer executor

-- Example 6: Multiline comment after the slash buffer executor
CREATE OR REPLACE PROCEDURE proc4 AS
BEGIN
  NULL;
END;
/
/*
  Multiline comment
  AFTER the slash buffer executor
*/

-- Example 7: Normal comment before the slash buffer executor
CREATE OR REPLACE PROCEDURE proc5 AS
BEGIN
  NULL;
END;
-- Comment before buffer executor
/

-- Example 8: Mixed comments
CREATE OR REPLACE PROCEDURE proc6 AS
BEGIN
  NULL;
END;
-- Comment before
/* Multiline before */
/
-- Comment after
/* Multiline after */

-- Example 9: Only comments between END and slash
CREATE OR REPLACE PROCEDURE proc7 AS
BEGIN
  NULL;
END;
-- Just a comment
/
