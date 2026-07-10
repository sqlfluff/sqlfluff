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
