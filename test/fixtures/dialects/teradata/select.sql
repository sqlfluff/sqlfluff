SELECT DATE;

CREATE TABLE t1 (f1 DATE);

SELECT DATE (FORMAT 'MMMbdd,bYYYY'); -- (CHAR(12), UC);  -- https://docs.teradata.com/r/S0Fw2AVH8ff3MDA0wDOHlQ/ryoeKJsEr22NqKahaktP5g
-- Disabled CHAR(12, UC) for now, see #1665

SELECT
    ADD_MONTHS(abandono.FEC_CIERRE_EST, -12) AS FEC_CIERRE_EST_ULT12,
    CAST('200010' AS DATE FORMAT 'YYYYMM') AS CAST_STATEMENT_EXAMPLE
FROM EXAMPLE_TABLE;

SEL * FROM CUSTOMERS;

SELECT * FROM CUSTOMERS;

SEL 1;

SELECT 1;

SELECT
    '9999-12-31' (DATE),
    '9999-12-31' (DATE FORMAT 'YYYY-MM-DD'),
    '100000' (SMALLINT)
from test_table;

select normalize on meets or overlaps
    id
    ,period(vld_fm, vld_to) as vld_prd
from mydb.mytable
where id = 12345;

SELECT NORMALIZE ON MEETS OR OVERLAPS emp_id, duration
FROM project;

SELECT NORMALIZE project_name, duration
FROM project;

SELECT NORMALIZE project_name, dept_id, duration
FROM project;

SELECT NORMALIZE ON OVERLAPS project_name, dept_id, duration
FROM project;

SELECT NORMALIZE ON OVERLAPS OR MEETS project_name, dept_id, duration
FROM project;

SELECT TOP 100 * FROM MY_TABLE;

SELECT * FROM MY_TABLE;

SELECT TOP 100
    COL_A,
    COL_B
FROM MY_TABLE;

SELECT DISTINCT *
FROM MY_TABLE;

SELECT TOP 10 PERCENT * FROM MY_TABLE;

SELECT TOP 0.1 PERCENT COL_A FROM MY_TABLE;

SELECT TOP 0.1 PERCENT WITH TIES COL_A, COL_B FROM MY_TABLE ORDER BY COL_B;
