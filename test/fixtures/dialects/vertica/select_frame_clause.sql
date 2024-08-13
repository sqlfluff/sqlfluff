-- https://docs.vertica.com/latest/en/sql-reference/functions/analytic-functions/

SELECT dev_group, product_name, users, ARGMAX(users, product_name) OVER (ORDER BY dev_group ASC) FROM service_info;
SELECT dev_group, product_name, users, ARGMIN(users, product_name) OVER (ORDER BY dev_group ASC) FROM service_info;

SELECT calendar_month_number_in_year Mo, SUM(product_price) Sales,
   AVG(SUM(product_price)) OVER (ORDER BY calendar_month_number_in_year
     ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING)::INTEGER Average
   FROM product_dimension pd, date_dimension dm, inventory_fact if
   WHERE dm.date_key = if.date_key AND pd.product_key = if.product_key GROUP BY Mo;

SELECT employee_region region, employee_key, annual_salary,
     RANK() OVER (PARTITION BY employee_region ORDER BY annual_salary) Rank,
     DENSE_RANK() OVER (PARTITION BY employee_region ORDER BY annual_salary) "Dense Rank"
     FROM employee_dimension;

SELECT customer_state, customer_key, annual_income, PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY annual_income)
      OVER (PARTITION BY customer_state) AS PERCENTILE_CONT
   FROM customer_dimension WHERE customer_state IN ('DC','WI') AND customer_key < 300
   ORDER BY customer_state, customer_key;

SELECT employee_last_name, annual_salary,
       STDDEV(annual_salary) OVER (ORDER BY hire_date) as "stddev"
   FROM employee_dimension
   WHERE job_title =  'Assistant Director';
