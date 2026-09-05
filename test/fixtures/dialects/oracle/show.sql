-- SQL*Plus SHOW command.
-- https://docs.oracle.com/en/database/oracle/oracle-database/26/sqpug/SHOW.html

SHOW ERRORS;

SHOW ERRORS FUNCTION my_func;

SHOW ERRORS PACKAGE BODY my_pkg;

SHOW PARAMETER;

SHOW PARAMETERS sga_target;

SHOW RECYCLEBIN;

SHOW ALL;

SHOW USER;

SHOW SGA;

SHOW RELEASE;

SHOW PDBS;

SHOW CON_NAME;

SHOW LINESIZE;

-- SHOW accepts SET system variables that are Oracle reserved words.
SHOW LONG;

SHOW NULL;

-- SQL*Plus terminates commands at newlines without requiring semicolons.
SHOW PARAMETERS
SHOW USER
SHOW PARAMETERS
SET SCAN ON
SHOW PARAMETERS
SELECT 1 FROM DUAL;
