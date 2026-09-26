MERGE INTO bonuses d
USING (SELECT employee_id, salary, department_id FROM employees) s
ON (d.employee_id = s.employee_id)
WHEN MATCHED THEN
    UPDATE SET d.bonus = d.bonus + s.salary * 0.01
    DELETE WHERE (s.salary > 8000);

MERGE INTO bonuses d
USING (SELECT employee_id, salary, department_id FROM employees) s
ON (d.employee_id = s.employee_id)
WHEN MATCHED THEN
    UPDATE SET d.bonus = d.bonus + s.salary * 0.01
    WHERE d.department_id = 80
    DELETE WHERE (s.salary > 8000)
WHEN NOT MATCHED THEN
    INSERT (d.employee_id, d.bonus)
    VALUES (s.employee_id, s.salary * 0.1)
    WHERE (s.salary <= 8000);
