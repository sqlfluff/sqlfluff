-- ?:: is shorthand for try_cast (an error-tolerating cast)
-- https://docs.databricks.com/aws/en/sql/language-manual/functions/questiondoublecolonsign
SELECT 1?::INT;

SELECT '20'?::INTEGER AS a;

SELECT 'twenty'?::INT AS maybe_null;

SELECT my_col?::STRING FROM my_table;

-- mixed with the standard :: cast operator
SELECT my_col::INT, my_col?::INT FROM my_table;
