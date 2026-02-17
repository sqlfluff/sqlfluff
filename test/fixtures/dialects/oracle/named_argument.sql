--https://docs.oracle.com/en/database/oracle/oracle-database/21/sqlrf/Function-Expressions.html

select my_function(arg1 => 3, arg2 => 4) from dual;

select my_function(3, arg2 => 4) from dual;

select my_function(arg1 => 3, 4) from dual;
