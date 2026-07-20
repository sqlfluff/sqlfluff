SELECT e.employee_id, e.salary, e.commission_pct
   FROM employees e, departments d
   WHERE job_id = 'SA_REP'
   AND e.department_id = d.department_id
   AND location_id = 2500
   ORDER BY e.employee_id
   FOR UPDATE;

SELECT e.employee_id, e.salary, e.commission_pct
   FROM employees e JOIN departments d
   USING (department_id)
   WHERE job_id = 'SA_REP'
   AND location_id = 2500
   ORDER BY e.employee_id
   FOR UPDATE OF e.salary;

SELECT employee_id FROM (SELECT * FROM employees)
   FOR UPDATE OF employee_id;

SELECT employee_id FROM (SELECT employee_id+1 AS employee_id FROM employees)
   FOR UPDATE;

SELECT e.salary FROM employees e
   WHERE e.employee_id = 100
   FOR UPDATE NOWAIT;

SELECT e.salary FROM employees e
   WHERE e.employee_id = 100
   FOR UPDATE OF e.salary NOWAIT;

SELECT e.salary FROM employees e
   WHERE e.employee_id = 100
   FOR UPDATE OF e.salary WAIT 5;

SELECT e.salary FROM employees e
   WHERE e.employee_id = 100
   FOR UPDATE SKIP LOCKED;
