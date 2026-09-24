DELETE FROM employees;

DELETE employees;

DELETE hr.employees WHERE employee_id = 100;

DELETE employees e WHERE e.department_id = 30;

DELETE FROM employees e WHERE e.department_id = 30;

DELETE employees
WHERE employee_id = 100
RETURNING last_name INTO :v_last_name;

BEGIN
    DELETE employees WHERE employee_id = 100;
END;
/
