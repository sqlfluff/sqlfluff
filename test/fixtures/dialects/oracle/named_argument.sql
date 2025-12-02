--https://docs.oracle.com/en/database/oracle/oracle-database/21/sqlrf/Function-Expressions.html#GUID-C47F0B7D-9058-481F-815E-A31FB21F3BD5

select my_function(arg1 => 3, arg2 => 4) from dual;

select my_function(3, arg2 => 4) from dual;

select my_function(arg1 => 3, 4) from dual;
