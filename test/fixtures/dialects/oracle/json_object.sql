SELECT JSON_OBJECT(
'name' : first_name || ' ' || last_name,
'email' : email,
'phone' : phone_number,
'hire_date' : hire_date
)
FROM employees
WHERE employee_id = 140;

SELECT JSON_OBJECT(*)
FROM employees
WHERE employee_id = 140;

SELECT JSON_OBJECT('NAME' VALUE first_name)
FROM employees e, departments d
WHERE e.department_id = d.department_id
AND e.employee_id = 140;

SELECT JSON_ARRAYAGG(JSON_OBJECT(*))
FROM departments;

SELECT JSON_OBJECT ('name' value 'Foo') FROM DUAL;

SELECT JSON_OBJECT ('name' value 'Foo' FORMAT JSON ) FROM DUAL;

SELECT JSON_OBJECT (
    KEY 'deptno' VALUE d.department_id,
    KEY 'deptname' VALUE d.department_name
    ) "Department Objects"
FROM departments d
ORDER BY d.department_id;

SELECT JSON_OBJECT(first_name, last_name, email, hire_date)
FROM employees
WHERE employee_id = 140;

SELECT JSON_OBJECT(eMail)
FROM employees
WHERE employee_id = 140;
