SELECT employee_last_name, SUM(vacation_days)
   FROM employee_dimension
   WHERE employee_last_name ILIKE 'S%'
   GROUP BY employee_last_name;

SELECT vendor_region, MAX(deal_size) AS "Biggest Deal"
   FROM vendor_dimension
   GROUP BY vendor_region;

SELECT vendor_region, MAX(deal_size) as "Biggest Deal"
   FROM vendor_dimension
   GROUP BY vendor_region
   HAVING MAX(deal_size) > 900000;

SELECT department, grants, SUM(apply_sum(grant_values))
   FROM employees
   GROUP BY grants, department;
