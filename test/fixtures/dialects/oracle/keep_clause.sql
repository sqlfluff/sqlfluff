SELECT
    employee_id,
    max(salary) KEEP (
        DENSE_RANK FIRST
        ORDER BY hire_date
    ) AS first_salary,
    max(salary) KEEP (
        DENSE_RANK FIRST
        ORDER BY hire_date NULLS LAST
    ) AS first_salary_no_null
FROM employees
GROUP BY employee_id;

SELECT
    employee_id,
    max(salary) KEEP (
        DENSE_RANK LAST
        ORDER BY hire_date NULLS FIRST
    ) AS last_salary,
    max(salary) KEEP (
        DENSE_RANK LAST
        ORDER BY hire_date NULLS FIRST
    ) AS last_salary_no_null
FROM employees
GROUP BY employee_id;

SELECT
    last_name,
    department_id,
    salary,

    min(salary) KEEP (
        DENSE_RANK FIRST
        ORDER BY commission_pct
    ) OVER (
        PARTITION BY department_id
    ) AS worst_salary,

    max(salary) KEEP (
        DENSE_RANK LAST
        ORDER BY commission_pct
    ) OVER (
        PARTITION BY department_id
    ) AS best_salary
FROM
    employees
ORDER BY
    department_id,
    salary,
    last_name;
