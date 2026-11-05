
CREATE OR REPLACE PACKAGE example_pkg AS
  PROCEDURE first_proc(p_value NUMBER);
  FUNCTION second_func RETURN NUMBER;
END example_pkg;
/
CREATE OR REPLACE PACKAGE BODY example_pkg AS
  PROCEDURE first_proc(p_value NUMBER) IS
    v_value NUMBER := p_value;
  BEGIN NULL; END first_proc;
  FUNCTION second_func RETURN NUMBER IS
  BEGIN RETURN 1; END second_func;
BEGIN NULL;
END example_pkg;
/
