CREATE TABLE cust_basic_profile AS SELECT
customer_key, customer_gender, customer_age, marital_status, annual_income, occupation
FROM customer_dimension WHERE customer_age>18 AND customer_gender !='';
