-- Test numeric literals including trailing decimal point (#8110)
SELECT 1. FROM dual;

SELECT 123. FROM dual;

SELECT 1.5 FROM dual;

SELECT 123e4 FROM dual;

SELECT 1.5e3 FROM dual;

SELECT 123 FROM dual;

SELECT 123.456 FROM dual;
