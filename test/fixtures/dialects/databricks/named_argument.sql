--https://docs.databricks.com/en/sql/language-manual/sql-ref-function-invocation.html#named-parameter-invocation

select my_function(arg1 => 3, arg2 => 4) from dual;

select my_function(3, arg2 => 4) from dual;

select my_function(arg1 => 3, 4) from dual;
