-- https://docs.snowflake.com/en/sql-reference/identifier-literal.html
-- Although IDENTIFIER(...) uses the syntax of a function, it is not a true function and is not returned by commands such as SHOW FUNCTIONS.
USE SCHEMA identifier('my_schema');

USE SCHEMA identifier('{{ params.schema_name }}');

create or replace database identifier('my_db');

create or replace schema identifier('my_schema');

create or replace table identifier('my_db.my_schema.my_table') (c1 number);

create or replace table identifier('"my_table"') (c1 number);

show tables in schema identifier('my_schema');

use schema identifier($schema_name);

insert into identifier($table_name) values (1), (2), (3);

select * from identifier($table_name) order by 1;

select * from identifier('my_table') order by 1;

select speed_of_light();

select identifier($my_function_name)();

select identifier('my_function_name')();

select identifier('my_function_name')(1, 2, 3);
