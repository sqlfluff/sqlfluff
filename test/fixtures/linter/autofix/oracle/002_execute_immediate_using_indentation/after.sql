DECLARE
    emp_count NUMBER;
    dept_id NUMBER := 10;
    min_salary NUMBER := 5000;
    emp_ids DBMS_SQL.NUMBER_TABLE;
    updated_ids DBMS_SQL.NUMBER_TABLE;
BEGIN
    EXECUTE IMMEDIATE
        'SELECT COUNT(*) FROM employees WHERE department_id = :1 AND salary >= :2'
        INTO emp_count
        USING dept_id, min_salary;

    EXECUTE IMMEDIATE
        'INSERT INTO audit_log VALUES (:1, :2, :3)'
        USING dept_id, min_salary, SYSDATE;

    EXECUTE IMMEDIATE
        'SELECT employee_id FROM employees WHERE department_id = :1'
        BULK COLLECT INTO emp_ids
        USING dept_id;

    EXECUTE IMMEDIATE
        'UPDATE employees SET salary = salary + 100 WHERE department_id = :1 RETURNING employee_id INTO :2'
        USING dept_id
        RETURNING BULK COLLECT INTO updated_ids;

    EXECUTE IMMEDIATE
        'DELETE FROM temp_employees WHERE department_id = :1 RETURNING employee_id, salary INTO :2, :3'
        USING dept_id
        RETURN BULK COLLECT INTO emp_ids, updated_ids;

    EXECUTE IMMEDIATE
        'UPDATE employees SET commission_pct = 0.05 WHERE employee_id = :1 RETURNING salary INTO :2'
        USING 100
        RETURN INTO emp_count;

    EXECUTE IMMEDIATE
        'INSERT INTO departments (department_id, department_name) VALUES (:1, :2) RETURNING department_id INTO :3'
        USING 999, 'Test Dept'
        RETURNING INTO dept_id;

    EXECUTE IMMEDIATE
        'UPDATE employees SET salary = :1, commission_pct = :2 WHERE department_id = :3 RETURNING employee_id, salary INTO :4, :5'
        USING 5000, 0.1, dept_id
        RETURN BULK COLLECT INTO emp_ids, updated_ids;
END;
/
