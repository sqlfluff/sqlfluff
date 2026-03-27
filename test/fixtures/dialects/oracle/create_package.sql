CREATE PACKAGE IF NOT EXISTS emp_mgmt AS
   FUNCTION hire (last_name VARCHAR2, job_id VARCHAR2,
      manager_id NUMBER, salary NUMBER,
      commission_pct NUMBER, department_id NUMBER)
      RETURN NUMBER;
   FUNCTION create_dept(department_id NUMBER, location_id NUMBER)
      RETURN NUMBER;
   PROCEDURE remove_emp(employee_id NUMBER);
   PROCEDURE remove_dept(department_id NUMBER);
   PROCEDURE increase_sal(employee_id NUMBER, salary_incr NUMBER);
   PROCEDURE increase_comm(employee_id NUMBER, comm_incr NUMBER);
   no_comm EXCEPTION;
   no_sal EXCEPTION;
END emp_mgmt;
/

-- Use of RESULT_CACHE keyword
CREATE OR REPLACE PACKAGE test_package IS

FUNCTION any_function_with_result_cache
RETURN VARCHAR2 RESULT_CACHE;

END test_package;
/

-- Use of POLYMORPHIC keyword
CREATE PACKAGE skip_col_pkg AS

  -- OVERLOAD 1: Skip by name --
  FUNCTION skip_col(tab TABLE,
                    col COLUMNS)
           RETURN TABLE PIPELINED ROW POLYMORPHIC USING skip_col_pkg;

  FUNCTION describe(tab IN OUT DBMS_TF.TABLE_T,
                    col        DBMS_TF.COLUMNS_T)
           RETURN DBMS_TF.DESCRIBE_T;

  -- OVERLOAD 2: Skip by type --
  FUNCTION skip_col(tab       TABLE,
                    type_name VARCHAR2,
                    flip      VARCHAR2 DEFAULT 'False')
           RETURN TABLE PIPELINED ROW POLYMORPHIC USING skip_col_pkg;

  FUNCTION describe(tab       IN OUT DBMS_TF.TABLE_T,
                    type_name        VARCHAR2,
                    flip             VARCHAR2 DEFAULT 'False')
           RETURN DBMS_TF.DESCRIBE_T;

END skip_col_pkg;
/
