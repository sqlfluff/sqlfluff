create or replace procedure sp_pi()
    returns float not null
    language javascript
    as
    $$
    return 3.1415926;
    $$
    ;

create or replace procedure stproc1(FLOAT_PARAM1 FLOAT)
    returns string
    language javascript
    strict
    execute as owner
    as
    $$
    var sql_command = 
     "INSERT INTO stproc_test_table1 (num_col1) VALUES (" + FLOAT_PARAM1 + ")";
    try {
        snowflake.execute (
            {sqlText: sql_command}
            );
        return "Succeeded.";   // Return a success/error indicator.
        }
    catch (err)  {
        return "Failed: " + err;   // Return a success/error indicator.
        }
    $$
    ;

CREATE OR REPLACE PROCEDURE public.test_procedure (test_table VARCHAR(), test_col VARCHAR())
RETURNS VARCHAR()
LANGUAGE JAVASCRIPT
AS
$$  
try {
    var sql_command = "ALTER TABLE " + test_table + " DROP " + tet_col;
    snowflake.execute ({sqlText: sql_command});
    return "Succeeded.";
}
catch (err) {
   return "Failed: execute "+ sql_command +". Error : "+ err;   // Return a success/error indicator.
}
$$
;



