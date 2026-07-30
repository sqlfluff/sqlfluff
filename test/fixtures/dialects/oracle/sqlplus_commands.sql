PROMPT this is an Oracle SQL newline delimited prompt statement
SET SCAN OFF
ACCEPT var
ACC short_var
ACCEPT myvar PROMPT 'Enter value; then press Enter'
REMARK
REMARK this is a SQL*Plus remark
REM
REM this is a SQL*Plus remark abbreviation
SELECT job_id FROM employees;

DECLARE
acc NUMBER;
BEGIN
NULL;
END;
/

DECLARE
rem NUMBER;
BEGIN
NULL;
END;
/

DECLARE
    acc := 1; -- comment
BEGIN
    NULL;
END;
/

DECLARE
    rem := 1; -- comment
BEGIN
    NULL;
END;
/

SHOW ERRORS
SHOW ALL
SHOW USER
SHOW SGA
SHOW PDBS
SHOW RELEASE
SHOW SQLCODE
SHOW EDITION
SHOW RECYCLEBIN
SHOW CON_NAME
SHOW PARAMETERS
SHOW PARAMETER db_name
SHOW ERRORS PROCEDURE my_proc
SHOW ERRORS PACKAGE BODY my_pkg
SHOW ERRORS TYPE BODY my_type
SHOW ERRORS FUNCTION myschema.my_fn
-- SQL*Plus accepts abbreviated option names
SHOW ERR
SHOW REL

DECLARE
show NUMBER;
BEGIN
NULL;
END;
/
