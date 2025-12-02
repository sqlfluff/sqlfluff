-- Pattern 1: Basic EXECUTE IMMEDIATE with concatenation
DECLARE
    constraint_name VARCHAR2(255);
    result_var NUMBER;
    table_name VARCHAR2(100) := 'MY_TABLE';
BEGIN
    SELECT constraint_name
    INTO constraint_name
    FROM user_constraints
    WHERE table_name = 'MY_TABLE'
        AND constraint_type = 'C'
        AND search_condition_vc LIKE 'MY_CONDITION%';

    EXECUTE IMMEDIATE 'ALTER TABLE ' || table_name ||
        ' DROP CONSTRAINT ' || constraint_name;
    EXECUTE IMMEDIATE 'ALTER TABLE MY_TABLE2 DROP CONSTRAINT ' ||
        constraint_name;
    EXECUTE IMMEDIATE 'SELECT COUNT(*) FROM ' || table_name
        INTO result_var;
    EXECUTE IMMEDIATE 'INSERT INTO MY_TABLE3 VALUES (:1, :2)'
        USING constraint_name, result_var;
    EXECUTE IMMEDIATE 'DROP TABLE MY_TABLE';
END;
/

-- Pattern 2: EXECUTE IMMEDIATE with variable expression
DECLARE
    a NUMBER := 4;
    b NUMBER := 7;
    plsql_block VARCHAR2(100);
BEGIN
    plsql_block := 'BEGIN calc_stats(:x, :x, :y, :x); END;';
    EXECUTE IMMEDIATE plsql_block USING a, b;
END;
/

-- Pattern 3: EXECUTE IMMEDIATE with unintialized variable
DECLARE
    a_null CHAR(1);  -- Set to NULL automatically at run time
BEGIN
    EXECUTE IMMEDIATE 'UPDATE employees_temp SET commission_pct = :x'
        USING a_null;
END;
/

-- Pattern 4: EXECUTE IMMEDIATE with IN OUT parameter modes
DECLARE
    plsql_block VARCHAR2(500);
    new_deptid NUMBER(4);
    new_dname VARCHAR2(30) := 'Advertising';
    new_mgrid NUMBER(6) := 200;
    new_locid NUMBER(4) := 1700;
BEGIN
    plsql_block := 'BEGIN create_dept(:a, :b, :c, :d); END;';
    EXECUTE IMMEDIATE plsql_block
        USING IN OUT new_deptid, new_dname, new_mgrid, new_locid;
END;
/

-- Pattern 5: EXECUTE IMMEDIATE with simple variable
DECLARE
    dyn_stmt VARCHAR2(200);
    b BOOLEAN := TRUE;
BEGIN
    dyn_stmt := 'BEGIN p(:x); END;';
    EXECUTE IMMEDIATE dyn_stmt USING b;
END;
/

-- Pattern 6: EXECUTE IMMEDIATE with OUT parameter mode
DECLARE
    r pkg.rec;
    dyn_str VARCHAR2(3000);
BEGIN
    dyn_str := 'BEGIN pkg.p(:x, 6, 8); END;';
    EXECUTE IMMEDIATE dyn_str USING OUT r;
    DBMS_OUTPUT.PUT_LINE('r.n1 = ' || r.n1);
    DBMS_OUTPUT.PUT_LINE('r.n2 = ' || r.n2);
END;
/

-- Pattern 7: EXECUTE IMMEDIATE with multiple parameters
DECLARE
    emp_count NUMBER;
    dept_id NUMBER := 10;
    min_salary NUMBER := 5000;
    dynamic_query VARCHAR2(500);
BEGIN
    dynamic_query := 'SELECT COUNT(*) ' ||
        'FROM employees ' ||
        'WHERE department_id = :dept_id ' ||
        'AND salary >= :min_salary';

    EXECUTE IMMEDIATE dynamic_query
        INTO emp_count
        USING dept_id, min_salary;

    DBMS_OUTPUT.PUT_LINE('Total employees found: ' || emp_count);
END;
/

-- Pattern 8: EXECUTE IMMEDIATE with BULK COLLECT INTO (simple arrays)
DECLARE
    emp_ids DBMS_SQL.NUMBER_TABLE;
    emp_names DBMS_SQL.VARCHAR2_TABLE;
    dept_id NUMBER := 20;
    dynamic_query VARCHAR2(500);
BEGIN
    dynamic_query := 'SELECT employee_id, first_name ' ||
        'FROM employees ' ||
        'WHERE department_id = :dept_id ' ||
        'AND rownum <= 10';

    EXECUTE IMMEDIATE dynamic_query
        BULK COLLECT INTO emp_ids, emp_names
        USING dept_id;

    FOR i IN 1..emp_ids.COUNT LOOP
        DBMS_OUTPUT.PUT_LINE('Employee: ' || emp_names(i) ||
            ' (ID: ' || emp_ids(i) || ')');
    END LOOP;

    DBMS_OUTPUT.PUT_LINE('Total employees found: ' || emp_ids.COUNT);
END;
/

-- Pattern 9: EXECUTE IMMEDIATE with UPDATE and RETURNING BULK COLLECT
DECLARE
    updated_ids DBMS_SQL.NUMBER_TABLE;
    updated_salaries DBMS_SQL.NUMBER_TABLE;
    dept_id NUMBER := 30;
    salary_increase NUMBER := 500;
    dynamic_update VARCHAR2(500);
BEGIN
    dynamic_update := 'UPDATE employees ' ||
        'SET salary = salary + :increase ' ||
        'WHERE department_id = :dept_id ' ||
        'AND salary < 8000 ' ||
        'RETURNING employee_id, salary INTO :ids, :salaries';

    EXECUTE IMMEDIATE dynamic_update
        USING salary_increase, dept_id
        RETURNING BULK COLLECT INTO updated_ids, updated_salaries;

    FOR i IN 1..updated_ids.COUNT LOOP
        DBMS_OUTPUT.PUT_LINE('Updated employee ID: ' || updated_ids(i) ||
            ', New salary: ' || updated_salaries(i));
    END LOOP;
END;
/

-- Pattern 10: EXECUTE IMMEDIATE with RETURN INTO
DECLARE
    emp_id NUMBER;
    emp_salary NUMBER;
    dynamic_delete VARCHAR2(500);
BEGIN
    dynamic_delete := 'DELETE FROM temp_employees ' ||
        'WHERE employee_id = :emp_id ' ||
        'RETURNING employee_id, salary INTO :id, :sal';

    EXECUTE IMMEDIATE dynamic_delete
        USING 100
        RETURN INTO emp_id, emp_salary;

    DBMS_OUTPUT.PUT_LINE('Deleted employee ID: ' || emp_id ||
        ', Salary was: ' || emp_salary);
END;
/

-- Pattern 11: EXECUTE IMMEDIATE with RETURNING INTO
DECLARE
    old_name VARCHAR2(100);
    new_salary NUMBER;
    dynamic_update VARCHAR2(500);
BEGIN
    dynamic_update := 'UPDATE employees ' ||
        'SET first_name = :new_name, salary = salary * 1.1 ' ||
        'WHERE employee_id = :emp_id ' ||
        'RETURNING first_name, salary INTO :name, :sal';

    EXECUTE IMMEDIATE dynamic_update
        USING 'John', 101
        RETURNING INTO old_name, new_salary;

    DBMS_OUTPUT.PUT_LINE('Updated employee: ' || old_name ||
        ', New salary: ' || new_salary);
END;
/
