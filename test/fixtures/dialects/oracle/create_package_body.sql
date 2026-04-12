-- Minimal package body (empty declarations, no init block)
CREATE PACKAGE BODY minimal_package IS
END minimal_package;
/

-- IF NOT EXISTS (Oracle 23c+): statement is silently ignored if body already exists
CREATE PACKAGE BODY IF NOT EXISTS minimal_package IS
END minimal_package;
/

-- Empty body using AS
CREATE OR REPLACE PACKAGE BODY minimal_as AS
END minimal_as;
/

-- Package body with only an initialization block (no declarations)
CREATE OR REPLACE PACKAGE BODY example AS
BEGIN
  NULL;
END example;
/

-- Package body with declarations and initialization block
CREATE OR REPLACE PACKAGE BODY full_example AS
  v_counter NUMBER := 0;
BEGIN
  v_counter := 1;
END full_example;
/

-- Package body with exception handler in initialization block
-- (division by zero is intentional: demonstrates WHEN OTHERS handler)
CREATE OR REPLACE PACKAGE BODY pkg_with_exception AS
  v_init NUMBER := 0;
BEGIN
  v_init := 1 / v_init;  -- always raises ORA-01476, caught below
EXCEPTION
  WHEN OTHERS THEN
    v_init := 0;
END pkg_with_exception;
/

-- Package body with subprogram definitions using sequences (no init block)
CREATE OR REPLACE PACKAGE BODY emp_mgmt AS
    tot_emps NUMBER;
    tot_depts NUMBER;

    FUNCTION hire
       (last_name VARCHAR2, job_id VARCHAR2,
        manager_id NUMBER, salary NUMBER,
        commission_pct NUMBER, department_id NUMBER)
       RETURN NUMBER IS
          new_empno NUMBER;
    BEGIN
       SELECT employees_seq.NEXTVAL
          INTO new_empno
          FROM DUAL;
       INSERT INTO employees
          VALUES (new_empno, 'First', 'Last', 'first.example@example.com',
                  '(415)555-0100',
                  TO_DATE('18-JUN-2002','DD-MON-YYYY'),
                  'IT_PROG', 90000000, 00, 100, 110);
       tot_emps := tot_emps + 1;
       RETURN(new_empno);
    END hire;

    FUNCTION create_dept(department_id NUMBER, location_id NUMBER)
       RETURN NUMBER IS
          new_deptno NUMBER;
    BEGIN
       SELECT departments_seq.NEXTVAL
          INTO new_deptno
          FROM dual;
       INSERT INTO departments
          VALUES (new_deptno, 'department name', 100, 1700);
       tot_depts := tot_depts + 1;
       RETURN(new_deptno);
    END create_dept;

    PROCEDURE remove_emp(employee_id NUMBER) IS
    BEGIN
       DELETE FROM employees
       WHERE employees.employee_id = remove_emp.employee_id;
       tot_emps := tot_emps - 1;
    END remove_emp;

    PROCEDURE remove_dept(department_id NUMBER) IS
    BEGIN
       DELETE FROM departments
       WHERE departments.department_id = remove_dept.department_id;
       tot_depts := tot_depts - 1;
       SELECT COUNT(*) INTO tot_emps FROM employees;
    END remove_dept;

    PROCEDURE increase_sal(employee_id NUMBER, salary_incr NUMBER) IS
       curr_sal NUMBER;
    BEGIN
       SELECT salary INTO curr_sal FROM employees
       WHERE employees.employee_id = increase_sal.employee_id;
       IF curr_sal IS NULL
          THEN RAISE no_sal;
       ELSE
          UPDATE employees
          SET salary = salary + salary_incr
          WHERE employee_id = employee_id;
       END IF;
    END increase_sal;

    PROCEDURE increase_comm(employee_id NUMBER, comm_incr NUMBER) IS
       curr_comm NUMBER;
    BEGIN
       SELECT commission_pct
       INTO curr_comm
       FROM employees
       WHERE employees.employee_id = increase_comm.employee_id;
       IF curr_comm IS NULL
          THEN RAISE no_comm;
       ELSE
          UPDATE employees
          SET commission_pct = commission_pct + comm_incr;
       END IF;
    END increase_comm;
END emp_mgmt;
/

-- Package body with nested BEGIN/END and multiple exception handlers
CREATE OR REPLACE PACKAGE BODY test_package IS

  FUNCTION test_function
  RETURN VARCHAR2 IS
    var_1 NUMBER := 0;
  BEGIN
    BEGIN
      SELECT 1 INTO var_1 FROM DUAL;
    EXCEPTION
      WHEN NO_DATA_FOUND THEN
        var_1 := 0;
      WHEN OTHERS THEN
        logger.log_error('Unhandled Exception');
        RAISE;
    END;
  END test_function;

END test_package;
/

-- DROP PACKAGE BODY
DROP PACKAGE BODY example;
