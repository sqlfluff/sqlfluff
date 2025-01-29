SELECT format('create index on my_table(%I)', attname)
FROM pg_attribute
WHERE attrelid = 'my_table'::regclass AND attnum > 0
ORDER BY attnum
\gexec

SELECT 'hello' AS var1, 10 AS var2
\gset

SELECT 'hello' AS var1, 10 AS var2
\gset result_

SELECT
    EXISTS(SELECT 1 FROM customer WHERE customer_id = 123) as is_customer,
    EXISTS(SELECT 1 FROM employee WHERE employee_id = 456) as is_employee
\gset

SELECT 'hello' AS my_psql_var \gset
SELECT :'my_psql_var';

SELECT relname, relkind FROM pg_class LIMIT 1 \gset

SELECT i FROM generate_series(1,2) i \gset prefix
